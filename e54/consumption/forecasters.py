import datetime
import io

import pandas as pd

from django.conf import settings

from consumption.api import RTE
from consumption.models import ConsumptionHistoricalData
from core.forecasters import Forecaster
from core.public_holidays import FrancePublicHolidays
from locations.models import Location
from weather.api import DarkSky
from weather.models import Weather

from .nn import ConsumptionInFranceNN


class ConsumptionInFranceForecaster(Forecaster):
    # Neural network
    nn_class = ConsumptionInFranceNN

    # Data information
    frequency = "30Min"

    def fetch_data(self):
        # Today's date
        today = datetime.date.today()

        # Locations
        france = Location.objects.get(name="France")
        paris = Location.objects.get(name="Paris")

        # Weather: prepare Dark Sky request
        latitude = paris.latitude
        longitude = paris.longitude
        time = today + datetime.timedelta(days=1)

        # Weather: fetch data from Dark Sky
        darksky = DarkSky()
        darksky.forecast(latitude, longitude, time)
        responses = darksky.fetch()

        # Weather: clean data
        data = pd.DataFrame(responses[0].json["hourly"]["data"])
        weather = pd.DataFrame(
            {
                "temperature": data["temperature"],
                "humidity": data["humidity"],
                "pressure": data["pressure"],
            }
        )
        weather.set_index(
            pd.to_datetime(data["time"], unit="s")
            .dt.tz_localize("UTC")
            .dt.tz_convert(settings.TIME_ZONE),
            inplace=True,
        )
        weather.drop_duplicates(inplace=True)

        # Weather: resample data
        start = today + datetime.timedelta(days=1)
        end = today + datetime.timedelta(days=2)
        datetimes = pd.date_range(
            start=start, end=end, freq=self.frequency, tz=settings.TIME_ZONE
        )[:-1]
        weather = weather.reindex(datetimes).interpolate()

        # Electrical consumption: prepare RTE request
        start_date = today - datetime.timedelta(days=6)
        end_date = today + datetime.timedelta(days=2)

        # Electrical consumption: fetch data from RTE
        rte = RTE()
        rte.get_consumption(type_="D-2", start_date=start_date, end_date=end_date)
        responses = rte.fetch()

        # Electrical consumption: format data
        data = pd.DataFrame(responses[0].json["short_term"][0]["values"])
        consumption = pd.DataFrame({"total": data["value"]})
        consumption.set_index(pd.to_datetime(data["start_date"]), inplace=True)
        consumption.drop_duplicates(inplace=True)

        # Electrical consumption: resample data
        start = start_date
        end = end_date
        datetimes = pd.date_range(
            start=start, end=end, freq=self.frequency, tz=settings.TIME_ZONE
        )[:-1]
        consumption = consumption.reindex(datetimes).interpolate()

        self.data = {"weather": weather, "consumption": consumption}

    def prepare_data(self):
        # Weather and electrical consumption data
        weather = self.data["weather"]
        consumption = self.data["consumption"]

        # Today's date
        today = datetime.date.today()

        # Datetimes range
        start = today - datetime.timedelta(days=6)
        end = today + datetime.timedelta(days=2)
        datetimes = pd.date_range(
            start=start, end=end, freq=self.frequency, tz=settings.TIME_ZONE
        )[:-1]

        # Date and time related arrays
        hour = datetimes.hour  # 0..24
        minute = datetimes.minute  # 0..59
        weekday = datetimes.weekday  # 0 (Monday)..6 (Sunday)
        day = datetimes.day  # 0..31
        month = datetimes.month  # 0..12

        # Public holidays
        # Note: public holidays in Alsace-Moselle are not considered
        # WARNING: this code works, but is ugly and should be rewritten
        is_public_holiday = pd.DataFrame(
            {"date": datetimes.date, "is_public_holiday": False}
        )
        for year in range(datetimes.min().year, datetimes.max().year + 1):
            for date in FrancePublicHolidays.for_year(year).values():
                is_public_holiday.loc[
                    is_public_holiday["date"] == pd.Timestamp(date).date(),
                    "is_public_holiday",
                ] = True
        is_public_holiday = is_public_holiday["is_public_holiday"].values

        # Public holidays on weekends (saturday or sunday)
        is_public_holiday_on_weekend = (
            (weekday == 5) | (weekday == 6)
        ) & is_public_holiday

        # Weather
        temperature = weather["temperature"] + 273.15  # [°C] -> [K]
        humidity = weather["humidity"]
        pressure = weather["pressure"]

        # Electrical consumption
        consumption = consumption["total"]
        consumption_d1 = consumption.shift(periods=48)
        consumption_w1 = consumption.shift(periods=48 * 7)

        # Final data
        input_data = pd.DataFrame(
            {
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "weekday": weekday,
                "is_public_holiday": is_public_holiday,
                "is_public_holiday_on_weekend": is_public_holiday_on_weekend,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "consumption_d1": consumption_d1,
                "consumption_w1": consumption_w1,
            }
        )[48 * 7 :]
        output_data = pd.DataFrame({"consumption": consumption})[48 * 7 :]

        self.input_data = input_data
        self.output_data = output_data
