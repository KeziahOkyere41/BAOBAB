# """Python API client wrapper for the PIDsLink Rest API."""

# import json
# import warnings

# import requests

# from .errors import PIDsLinkError
# from .request import PIDsLinkRequest

# HTTP_OK = requests.codes["ok"]
# HTTP_CREATED = requests.codes["created"]

# class PIDsLinkRESTClient(object):
#     """PIDsLink REST API client wrapper."""

#     def __init__(
#         self, username, password, prefix, test_mode=False, url=None, timeout=None
#     ):
#         """Initialize the REST client wrapper.

#         :param username: PIDsLink username.
#         :param password: PIDsLink password.
#         :param prefix: ARK prefix (or CFG_PIDSLINK_ARK_PREFIX).
#         :param test_mode: use test URL when True
#         :param url: PIDsLink API base URL.
#         :param timeout: Connect and read timeout in seconds. Specify a tuple
#             (connect, read) to specify each timeout individually.
#         """
#         self.username = str(username)
#         self.password = str(password)
#         self.prefix = str(prefix)

#         if test_mode:
#             self.api_url = "https://pidslinkapi.ren.africa/"
#         else:
#             self.api_url = url or "https://pidslinkapi.ren.africa/"

#         if not self.api_url.endswith("/"):
#             self.api_url += "/"

#         self.timeout = timeout

#     def __repr__(self):
#         """Create string representation of object."""
#         return "<PIDsLinkRESTClient: {0}>".format(self.username)

#     def _create_request(self):
#         """Create a new Request object."""
#         return PIDsLinkRequest(
#             base_url=self.api_url,
#             username=self.username,
#             password=self.password,
#             timeout=self.timeout,
#         )

#     def get_ark(self, ark):
#         """Get the URL where the resource pointed by the ARK is located.

#         :param ark: ARK name of the resource.
#         """
#         request = self._create_request()
#         resp = request.get("api/pids/query/{pidsId}/" + ark)
#         if resp.status_code == HTTP_OK:
#             return resp.json()["data"]["attributes"]["url"]
#         else:
#             raise PIDsLinkError.factory(resp.status_code, resp.text)

#     def post_ark(self, data):
#         """Post a new JSON payload to PIDsLink."""
#         headers = {
#             'content-type': 'application/json',
#             'accept': 'application/json',
#         }
#         body = {"data": data}
#         request = self._create_request()
#         resp = request.post(
#             "api/pids/mint/", 
#             body=json.dumps(body), 
#             headers=headers)
#         if resp.status_code == HTTP_CREATED:
#             return resp.json()["data"]["ark"]
#         else:
#             raise PIDsLinkError.factory(resp.status_code, resp.text)

#     def put_ark(self, ark, data):
#         """Put a JSON payload to PIDsLink for an existing ARK."""
#         headers = {
#             'content-type': 'application/json',
#             'accept': 'application/json',
#         }
#         body = {"data": data}
#         request = self._create_request()
#         url = "api/pids/update/{pidsId}" + ark
#         resp = request.put(url, body=json.dumps(body), headers=headers)
#         if resp.status_code == HTTP_OK:
#             return resp.json()["data"]["ark"]
#         else:
#             raise PIDsLinkError.factory(resp.status_code, resp.text)

import json
import requests

from .errors import PIDsLinkError
from .request import PIDsLinkRequest

HTTP_OK = requests.codes["ok"]
HTTP_CREATED = requests.codes["created"]

class PIDsLinkRESTClient(object):
    """PIDsLink REST API client wrapper."""

    def __init__(
        self, username, password, prefix, test_mode=False, url=None, timeout=None
    ):
        """Initialize the REST client wrapper.

        :param username: PIDsLink username.
        :param password: PIDsLink password.
        :param prefix: ARK prefix (or CFG_PIDSLINK_ARK_PREFIX).
        :param test_mode: use test URL when True
        :param url: PIDsLink API base URL.
        :param timeout: Connect and read timeout in seconds. Specify a tuple
            (connect, read) to specify each timeout individually.
        """
        self.username = str(username)
        self.password = str(password)
        self.prefix = str(prefix)

        if test_mode:
            self.api_url = "https://pidslinkapi.ren.africa/"
        else:
            self.api_url = url or "https://pidslinkapi.ren.africa/"

        if not self.api_url.endswith("/"):
            self.api_url += "/"

        self.timeout = timeout

    def __repr__(self):
        """Create string representation of object."""
        return "<PIDsLinkRESTClient: {0}>".format(self.username)

    def _create_request(self):
        """Create a new Request object."""
        return PIDsLinkRequest(
            base_url=self.api_url,
            username=self.username,
            password=self.password,
            timeout=self.timeout,
        )

    def get_pids(self, pids_id):
        """Get details of a PIDs.

        :param pids_id: ID of the PIDs.
        """
        request = self._create_request()
        resp = request.get(f"api/pids/query/{pids_id}/")
        if resp.status_code == HTTP_OK:
            return resp.json()["data"]
        else:
            raise PIDsLinkError.factory(resp.status_code, resp.text)

    def post_pids(self, naan, shoulder, url, metadata, type_, commitment, identifier, format_, relation, source):
        """Post a new JSON payload to mint PIDs."""
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
        }
        data = {
            "naan": naan,
            "shoulder": shoulder,
            "url": url,
            "metadata": metadata,
            "type": type_,
            "commitment": commitment,
            "identifier": identifier,
            "format": format_,
            "relation": relation,
            "source": source
        }
        request = self._create_request()
        resp = request.post(
            "api/pids/mint/",
            body=json.dumps(data),
            headers=headers
        )
        if resp.status_code == HTTP_CREATED:
            return resp.json()["data"]["pids_id"]
        else:
            raise PIDsLinkError.factory(resp.status_code, resp.text)

    def patch_pids(self, pids_id, url=None, metadata=None, type_=None, commitment=None, identifier=None, format_=None, relation=None, source=None):
        """Patch an existing PIDs with new data."""
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
        }
        data = {
            "url": url,
            "metadata": metadata,
            "type": type_,
            "commitment": commitment,
            "identifier": identifier,
            "format": format_,
            "relation": relation,
            "source": source
        }
        # Remove keys with value None to avoid sending empty fields
        data = {k: v for k, v in data.items() if v is not None}
        
        request = self._create_request()
        url_path = f"api/pids/update/{pids_id}"
        resp = request.patch(url_path, body=json.dumps(data), headers=headers)
        if resp.status_code == HTTP_OK:
            return resp.json()["data"]["pids_id"]
        else:
            raise PIDsLinkError.factory(resp.status_code, resp.text)
