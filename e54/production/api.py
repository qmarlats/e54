import itertools

from core.api import API, Request


class Opendatasoft(API):
    # API information
    api_name = "Opendatasoft"
    base_url = "https://data.opendatasoft.com/api/v2/catalog/datasets"

    # Authentication information
    authentication_method = "key"

    def export_la_haute_borne_data(self, **kwargs):
        # API resource endpoint
        endpoint = "la-haute-borne-data-2017-2020@engie-darwin4res/exports/json"

        # Note: no API key needed

        # API resource URL
        url = self.build_url(endpoint, **kwargs)

        # Stack request
        self.requests.append(Request(url))


class ReseauxEnergies(API):
    # API information
    api_name = "ReseauxEnergies"
    base_url = "https://opendata.reseaux-energies.fr/api/v2/catalog/datasets"

    # Authentication information
    authentication_method = "key"

    def export_eco2mix_regional_consumption(self, **kwargs):
        # API resource endpoint
        endpoint = "eco2mix-regional-cons-def/exports/json"

        # API resource parameters
        parameters = {"apikey": self.api_key}
        parameters.update(**kwargs)

        # API resource URL
        url = self.build_url(endpoint, **parameters)

        # Stack request
        self.requests.append(Request(url))
