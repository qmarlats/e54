import asyncio
from abc import ABC
from configparser import ConfigParser

from aiohttp import ClientSession
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# File containing API credentials
API_CREDENTIALS_PATH = ".api_credentials"


class API(ABC):
    def __init__(self):
        # Initialize empty headers dictionary and requests list
        self.headers = {}
        self.requests = []

        # Authenticate
        self.authenticate()

    def authenticate(self):
        # Read API credentials
        api_credentials = ConfigParser()
        api_credentials.read(API_CREDENTIALS_PATH)
        api_credentials = api_credentials[self.api_name]

        # API key authentication
        if self.authentication_method == "key":
            # Retrieve API key
            self.api_key = api_credentials.get("key")

        # Oauth 2.0 authentication
        elif self.authentication_method == "oauth2":
            # Retrieve API credentials
            client_id = api_credentials.get("client_id")
            client_secret = api_credentials.get("client_secret")

            # Initialize OAuth 2.0 session
            client = BackendApplicationClient(client_id=client_id)
            session = OAuth2Session(client=client)

            # Fetch token
            raw_token = session.fetch_token(
                token_url=self.token_url,
                client_id=client_id,
                client_secret=client_secret,
            )
            access_token = raw_token["access_token"]
            token_type = raw_token["token_type"]

            # Update authentication header
            self.headers["Authorization"] = f"{token_type} {access_token}"

    def build_url(self, *args, **kwargs):
        # API URL
        url = self.base_url

        # Resource URL
        if args:
            url += "/" + "/".join(args)

        # Parameters
        if kwargs:
            url += "?"  # Parameters separator
            for key, value in kwargs.items():
                if value:
                    url += f"{key}={value}&"
            url = url.rstrip("&")  # Remove last ampersand

        return url

    def fetch(self, authenticate=True):
        async def _fetch(session, url):
            async with session.get(url) as response:
                return Response(await response.json(), await response.text())

        async def _fetch_all():
            async with ClientSession(headers=self.headers) as session:
                return await asyncio.gather(
                    *[_fetch(session, request.url) for request in self.requests]
                )

        return asyncio.run(_fetch_all())


class Request:
    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url


class Response:
    def __init__(self, json, text):
        self._json = json
        self._text = text

    @property
    def json(self):
        return self._json

    @property
    def text(self):
        return self._text
