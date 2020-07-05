import pandas as pd
from django.conf import settings

from core.api import API, Request


class RTE(API):
    # API information
    api_name = "RTE"
    base_url = "https://digital.iservices.rte-france.com/open_api"

    # Authentication information
    authentication_method = "oauth2"
    token_url = "https://digital.iservices.rte-france.com/token/oauth"

    def get_consolidated_consumption(self, start_date=None, end_date=None, **kwargs):
        # API resource endpoint
        endpoint = "consolidated_consumption/v1/consolidated_power_consumption"

        # Format dates
        if start_date:
            start_date = pd.Timestamp(start_date, tz=settings.TIME_ZONE).isoformat()
        if end_date:
            end_date = pd.Timestamp(end_date, tz=settings.TIME_ZONE).isoformat()

        # API resource parameters
        parameters = {"start_date": start_date, "end_date": end_date}
        parameters.update(**kwargs)

        # API resource URL
        url = self.build_url(endpoint, **parameters)

        # Stack request
        self.requests.append(Request(url))

    def get_consumption(self, type_=None, start_date=None, end_date=None, **kwargs):
        # API resource endpoint
        endpoint = "consumption/v1/short_term"

        # Format dates
        if start_date:
            start_date = pd.Timestamp(start_date, tz=settings.TIME_ZONE).isoformat()
        if end_date:
            end_date = pd.Timestamp(end_date, tz=settings.TIME_ZONE).isoformat()

        # API resource parameters
        parameters = {"type": type_, "start_date": start_date, "end_date": end_date}
        parameters.update(**kwargs)

        # API resource URL
        url = self.build_url(endpoint, **parameters)

        # Stack request
        self.requests.append(Request(url))
