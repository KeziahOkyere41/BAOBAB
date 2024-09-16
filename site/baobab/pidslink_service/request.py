import ssl
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import json  # Ensure json is imported

from .errors import HttpError


class PIDsLinkRequest(object):
    """Helper class for making requests.

    :param base_url: Base URL for all requests.
    :param username: HTTP Basic Authentication Username
    :param password: HTTP Basic Authentication Password
    :param default_params: A key/value-mapping which will be converted into a
        query string on all requests.
    :param timeout: Connect and read timeout in seconds. Specify a tuple
        (connect, read) to specify each timeout individually.
    """

    def __init__(
        self,
        base_url=None,
        username=None,
        password=None,
        default_params=None,
        timeout=None,
    ):
        """Initialize request object."""
        self.base_url = base_url
        self.username = username
        self.password = password.encode("utf8")
        self.default_params = default_params or {}
        self.timeout = timeout

    def request(self, url, method="GET", body=None, params=None, headers=None):
        """Make a request.

        If the request was successful (i.e no exceptions), you can find the
        HTTP response code in self.code and the response body in self.value.

        :param url: Request URL (relative to base_url if set)
        :param method: Request method (GET, POST, PATCH) supported
        :param body: Request body
        :param params: Request parameters
        :param headers: Request headers
        """
        params = params or {}
        headers = headers or {}

        if self.default_params:
            params.update(self.default_params)

        if self.base_url:
            url = self.base_url + url

        request_func = getattr(requests, method.lower())
        kwargs = dict(
            auth=HTTPBasicAuth(self.username, self.password),
            params=params,
            headers=headers,
        )

        if method in ["POST", "PATCH"]:
            kwargs["data"] = body  # Use 'data' for POST and PATCH

        if self.timeout is not None:
            kwargs["timeout"] = self.timeout

        try:
            response = request_func(url, **kwargs)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except RequestException as e:
            raise HttpError(e)
        except ssl.SSLError as e:
            raise HttpError(e)

    def post(self, url, naan, shoulder, url_value, metadata, type_, commitment, identifier, format_, relation, source, headers=None):
        """Make a POST request."""
        body = json.dumps({
            "naan": naan,
            "shoulder": shoulder,
            "url": url_value,
            "metadata": metadata,
            "type": type_,
            "commitment": commitment,
            "identifier": identifier,
            "format": format_,
            "relation": relation,
            "source": source
        })
        headers = headers or {"Content-Type": "application/json"}
        return self.request(
            url, method="POST", body=body, headers=headers
        )

    def patch(self, url, url_value, metadata, type_, commitment, identifier, format_, relation, source, headers=None):
        """Make a PATCH request."""
        body = json.dumps({
            "url": url_value,
            "metadata": metadata,
            "type": type_,
            "commitment": commitment,
            "identifier": identifier,
            "format": format_,
            "relation": relation,
            "source": source
        })
        headers = headers or {"Content-Type": "application/json"}
        return self.request(
            url, method="PATCH", body=body, headers=headers
        )
