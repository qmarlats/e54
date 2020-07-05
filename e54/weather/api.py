import pandas as pd

from core.api import API, Request


class DarkSky(API):
    # API information
    api_name = "DarkSky"
    base_url = "https://api.darksky.net"

    # Authentication information
    authentication_method = "key"

    def forecast(self, latitude, longitude, time=None, **kwargs):
        # API resource endpoint
        endpoint = f"forecast/{self.api_key}"

        # Append latitude and longitude to the endpoint
        endpoint += f"/{latitude},{longitude}"

        # If time is given (ie. “Time Machine Request”)
        if time:
            # Format date
            time = pd.Timestamp(time).isoformat()

            # Append time to the endpoint
            endpoint += f",{time}"

        # API resource parameters
        parameters = {
            "exclude": kwargs.get("exclude", ""),
            "lang": kwargs.get("lang", "en"),
            "units": kwargs.get("units", "si"),
        }
        parameters.update(**kwargs)

        # API resource URL
        url = self.build_url(endpoint, **parameters)

        # Stack request
        self.requests.append(Request(url))


class Forecast:
    def __init__(self, raw):
        self.latitude = raw["latitude"]
        self.longitude = raw["longitude"]
        self.timezone = raw["timezone"]
        self.currently = raw.get("currently")
        self.minutely = raw.get("minutely")
        self.hourly = raw.get("hourly")
        self.daily = raw.get("daily")
