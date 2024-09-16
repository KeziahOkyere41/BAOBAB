# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2023 Northwestern University.
# Copyright (C) 2023-2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PIDsLink ARK Provider."""
import json
import warnings
import requests
from flask import current_app
from invenio_pidstore.models import PIDStatus

from baobab.pidslink_service.rest_client import PIDsLinkRESTClient
from baobab.pidslink_service.errors import PIDsLinkError, PIDsLinkNoContentError, PIDsLinkServerError
from invenio_rdm_records.services.pids.providers import PIDProvider


class PIDsLinkClient:
    """PIDsLink Client."""

    def __init__(self, name, config_prefix=None, **kwargs):
        """Constructor."""
        self.name = name
        self._config_prefix = config_prefix or "PIDSLINK"
        self._api = "None"
        print(f"[INIT] Initialized PIDsLinkClient with name: {self.name}, config_prefix: {self._config_prefix}")

    def cfgkey(self, key):
        """Generate a configuration key."""
        config_key = f"{self._config_prefix}_{key.upper()}"
        print(f"[CFGKEY] Generated config key: {config_key}")
        return f"{self._config_prefix}_{key.upper()}"

    def cfg(self, key, default=None):
        """Get an application config value."""
        return current_app.config.get(self.cfgkey(key), default)

    def generate_ark(record):
        """Generate an ARK identifier."""
        print(f"[GENERATE_ARK] Starting ARK generation for record: {record}")
        

        url = f"https://baobabtest.wacren.net/records/{record.pid.pid_value}"
        print(f"[GENERATE_ARK] Generated record URL: {url}")

        body = {
            'naan': "50962",
            'shoulder': "/bb67854",
            'url': url,
            'metadata': "",
            'type': "",
            'commitment': "",
            'identifier': "",
            'format': "",
            'relation': "",
            'source': url
        }
        print(f"[GENERATE_ARK] Prepared request body: {body}")

        base_url = "https://pidslinkapi.ren.africa/api/pids/mint/baobab"
        print(f"[GENERATE_ARK] Sending POST request to: {base_url}")
        response = requests.post(base_url, json=body)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to generate ARK. Status code: {response.status_code}, Response: {response.text}")

        response_data = response
        ark_format = response_data.ark

        if not ark_format:
            raise RuntimeError("ARK format not found in the response.")

        return ark_format

    def check_credentials(self, **kwargs):
        """Check if the client has the necessary credentials set up.

        If the client is running in test mode, credentials are not required.
        """
        if not (self.cfg("username") and self.cfg("password") and self.cfg("prefix")):
            warnings.warn(
                f"The {self.__class__.__name__} is misconfigured. Please "
                f"set {self.cfgkey('username')}, {self.cfgkey('password')}"
                f" and {self.cfgkey('prefix')} in your configuration.",
                UserWarning,
            )

    @property
    def api(self):
        """PIDsLink REST API client instance."""
        if self._api is None:
            self.check_credentials()
            self._api = PIDsLinkRESTClient(
                self.cfg("username"),
                self.cfg("password"),
                self.cfg("prefix"),
                self.cfg("test_mode", True),
            )
        return self._api


class PIDsLinkPIDProvider(PIDProvider):
    """PIDsLink Provider class.

    Note that PIDsLink is only contacted when an ARK is reserved or
    registered, or any action posterior to it. Its creation happens
    only at PIDStore level.
    """

    name = "ark"

    def __init__(
        self,
        id_,
        client=None,
        pid_type="ark",
        default_status=PIDStatus.NEW,
        **kwargs,
    ):
        """Constructor."""
        super().__init__(
            id_,
            client=(client or PIDsLinkClient("pidslink", config_prefix="PIDSLINK")),
            pid_type=pid_type,
            default_status=PIDStatus.NEW,
            managed=True,
            **kwargs
        )

    @staticmethod
    def _log_errors(exception):
        """Log errors from PIDsLinkError class."""
        ex_txt = exception.args[0] or ""
        if isinstance(exception, PIDsLinkNoContentError):
            current_app.logger.error(f"No content error: {ex_txt}")
        elif isinstance(exception, PIDsLinkServerError):
            current_app.logger.error(f"PIDsLink internal server error: {ex_txt}")
        else:
            # Client error 4xx status code
            try:
                ex_json = json.loads(ex_txt)
            except JSONDecodeError:
                current_app.logger.error(f"Unknown error: {ex_txt}")
                return

            # the `errors` field is only available when a 4xx error happened (not 500)
            for error in ex_json.get("errors", []):
                reason = error["title"]
                field = error.get("source")  # set when missing/wrong required field
                error_prefix = f"Error in `{field}`: " if field else "Error: "
                current_app.logger.error(f"{error_prefix}{reason}")

    def generate_id(self, record, **kwargs):
        """Generate a unique ARK."""
        # Delegate to client
        return self.client.generate_ark(record)

    @classmethod
    def is_enabled(cls, app):
        """Determine if pidslink is enabled or not."""
        return app.config.get("PIDSLINK_ENABLED", True)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered() and not pid.is_reserved()

    def register(self, pid, record, **kwargs):
        """Register an ARK via the PIDsLink API.

        :param pid: the PID to register.
        :param record: the record metadata for the ARK.
        :returns: `True` if it is registered successfully.
        """
        if isinstance(record, ChainObject):
            if record._child["access"]["record"] == "restricted":
                return False
        elif record["access"]["record"] == "restricted":
            return False

        local_success = super().register(pid)
        if not local_success:
            return False

        try:
            doc = self.serializer.dump_obj(record)
            url = kwargs["url"]
            self.name.api.post(metadata=doc, url=url, ark=pid.pid_value)
            return True
        except PIDsLinkError as e:
            current_app.logger.warning(
                f"PIDsLink provider error when registering ARK for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

    def update(self, pid, record, url=None, **kwargs):
        """Update metadata associated with an ARK.

        This can be called before/after an ARK is registered.
        :param pid: the PID to register.
        :param record: the record metadata for the ARK.
        :returns: `True` if it is updated successfully.
        """
        hide = False
        if isinstance(record, ChainObject):
            if record._child["access"]["record"] == "restricted":
                hide = True
        elif record["access"]["record"] == "restricted":
            hide = True

        try:
            if hide:
                self.client.api.hide_ark(ark=pid.pid_value)
            else:
                doc = self.serializer.dump_obj(record)
                doc["event"] = (
                    "publish"  # Required for ARK to make the ARK findable in the case it was hidden before.
                )
                self.client.api.update_ark(metadata=doc, ark=pid.pid_value, url=url)
        except PIDsLinkError as e:
            current_app.logger.warning(
                f"PIDsLink provider error when updating ARK for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

        if pid.is_deleted():
            return pid.sync_status(PIDStatus.REGISTERED)

        return True


    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). `success` is a bool that specifies
                  if the validation was successful. `errors` is a list of
                  error dicts of the form:
                  `{"field": <field>, "messages: ["<msgA1>", ...]}`.
        """
        # success is unused, but naming it _ would interfere with lazy_gettext as _
        success, errors = super().validate(record, identifier, provider, **kwargs)

        # Validate identifier
        # Checking if the identifier is not None is crucial because not all records at
        # this point will have an ARK identifier (and that is fine in the case of initial
        # creation)
        if identifier is not None:
            # Format check
            try:
                self.client.api.check_ark(identifier)
            except ValueError as e:
                # modifies the error in errors in-place
                self._insert_pid_type_error_msg(errors, str(e))

        # Validate record
        if not record.get("metadata", {}).get("publisher"):
            errors.append(
                {
                    "field": "metadata.publisher",
                    "messages": [
                        _("Missing publisher field required for ARK registration.")
                    ],
                }
            )

        return not bool(errors), errors

    def validate_restriction_level(self, record, identifier=None, **kwargs):
        """Remove the ARK if the record is restricted."""
        if identifier and record["access"]["record"] == "restricted":
            pid = self.get(identifier)
            if pid.status in [PIDStatus.NEW]:
                self.delete(pid)
                del record["pids"][self.pid_type]

    def create_and_reserve(self, record, **kwargs):
        """Create and reserve an ARK for the given record, and update the record with the reserved ARK."""
        if "ark" not in record.pids:
            pid = self.create(record)
            self.reserve(pid, record=record)
            pid_attrs = {"identifier": pid.pid_value, "provider": self.name}
            if self.client:
                pid_attrs["client"] = self.client.name
            record.pids["ark"] = pid_attrs


# class PIDsLinkClient:
#     """PIDsLink Client."""

#     def __init__(self, name, config_prefix=None, **kwargs):
#         """Constructor."""
#         self.name = name
#         self._config_prefix = config_prefix or "PIDSLINK"
#         self._api = None
#         print(f"[INIT] Initialized PIDsLinkClient with name: {self.name}, config_prefix: {self._config_prefix}")

#     def cfgkey(self, key):
#         """Generate a configuration key."""
#         config_key = f"{self._config_prefix}_{key.upper()}"
#         print(f"[CFGKEY] Generated config key: {config_key}")
#         return config_key

#     def cfg(self, key, default=None):
#         """Get an application config value."""
#         value = current_app.config.get(self.cfgkey(key), default)
#         print(f"[CFG] Retrieved config value for key: {key}, value: {value}")
#         return value

#     def generate_ark(self, record):
#         """Generate an ARK identifier."""
#         print(f"[GENERATE_ARK] Starting ARK generation for record: {record}")
        
#         # Prepare the URL for the ARK identifier
#         url = f"https://baobabtest.wacren.net/records/{record.pid.pid_value}"
#         print(f"[GENERATE_ARK] Generated record URL: {url}")

#         # Prepare the request body
#         body = {
#             'naan': "50962",
#             'shoulder': "/bb67854",
#             'url': url,
#             'metadata': "",
#             'type': "",
#             'commitment': "",
#             'identifier': "",
#             'format': "",
#             'relation': "",
#             'source': url
#         }
#         print(f"[GENERATE_ARK] Prepared request body: {body}")

#         # Make a POST request to mint a new ARK
#         base_url = "https://pidslinkapi.ren.africa/api/pids/mint/baobab"
#         print(f"[GENERATE_ARK] Sending POST request to: {base_url}")
#         response = requests.post(base_url, json=body)

#         print(f"[GENERATE_ARK] Response Status Code: {response.status_code}")
#         try:
#             response_data = response.json()  # Try to parse the response as JSON
#             print(f"[GENERATE_ARK] Response JSON: {response_data}")
#         except ValueError:
#             raise RuntimeError(f"[GENERATE_ARK] Failed to decode JSON. Response: {response.text}")

#         # Check for a successful response
#         if response.status_code != 200:
#             raise RuntimeError(f"[GENERATE_ARK] Failed to generate ARK. Status code: {response.status_code}, Response: {response.text}")

#         # Extract the ARK from the response
#         ark_format = response_data.get("ark")
#         print(f"[GENERATE_ARK] Extracted ARK format: {ark_format}")

#         if not ark_format:
#             raise RuntimeError("[GENERATE_ARK] ARK format not found in the response.")
        
#         print(f"[GENERATE_ARK] Successfully generated ARK: {ark_format}")
#         return ark_format

#     def update_ark(self, pids_id, record, url=None):
#         """Update metadata for an existing ARK."""
#         print(f"[UPDATE_ARK] Starting update for ARK with PID ID: {pids_id}, URL: {url}")

#         # Prepare the update request body
#         body = {
#             'url': url,
#             'metadata': "",  # Add necessary metadata fields
#             'type': "",
#             'commitment': "",
#             'identifier': "",
#             'format': "",
#             'relation': "",
#             'source': url
#         }
#         print(f"[UPDATE_ARK] Prepared request body: {body}")

#         # Make a PUT request to update the ARK
#         update_url = f"https://pidslinkapi.ren.africa/api/pids/update/{pids_id}"
#         print(f"[UPDATE_ARK] Sending PUT request to: {update_url}")
#         response = requests.put(update_url, json=body)

#         print(f"[UPDATE_ARK] Response Status Code: {response.status_code}")
#         if response.status_code != 200:
#             raise RuntimeError(f"[UPDATE_ARK] Failed to update ARK. Status code: {response.status_code}, Response: {response.text}")

#         print(f"[UPDATE_ARK] Successfully updated ARK with PID ID: {pids_id}")
#         return True

#     def check_credentials(self, **kwargs):
#         """Check if the client has the necessary credentials set up.

#         If the client is running in test mode, credentials are not required.
#         """
#         print(f"[CHECK_CREDENTIALS] Checking credentials...")
#         if not (self.cfg("username") and self.cfg("password") and self.cfg("prefix")):
#             warnings.warn(
#                 f"[CHECK_CREDENTIALS] The {self.__class__.__name__} is misconfigured. Please set "
#                 f"{self.cfgkey('username')}, {self.cfgkey('password')}, and {self.cfgkey('prefix')} "
#                 "in your configuration.",
#                 UserWarning,
#             )
#         print(f"[CHECK_CREDENTIALS] Credentials check complete.")

#     @property
#     def api(self):
#         """PIDsLink REST API client instance."""
#         if self._api is None:
#             print(f"[API] Initializing PIDsLinkRESTClient...")
#             self.check_credentials()
#             self._api = PIDsLinkRESTClient(
#                 self.cfg("username"),
#                 self.cfg("password"),
#                 self.cfg("prefix"),
#                 self.cfg("test_mode", True),
#             )
#             print(f"[API] PIDsLinkRESTClient initialized.")
#         return self._api



# class PIDsLinkPIDProvider(PIDProvider):
#     """PIDsLink Provider class."""

#     name = "ark"

#     def __init__(
#         self,
#         id_,
#         client=None,
#         pid_type="ark",
#         default_status=PIDStatus.NEW,
#         **kwargs,
#     ):
#         """Constructor."""
#         super().__init__(
#             id_,
#             client=(client or PIDsLinkClient("pidslink", config_prefix="PIDSLINK")),
#             pid_type=pid_type,
#             default_status=PIDStatus.NEW,
#             managed=True,
#             **kwargs
#         )

#     def generate_id(self, record, **kwargs):
#         print("[GENERATE_ID] generate_id method called")
#         pid_value = self.client.generate_ark(record)
#         print(f"[GENERATE_ID] Generated PID value: {pid_value}")
#         return pid_value

#     @classmethod
#     def is_enabled(cls, app):
#         """Determine if pidslink is enabled or not."""
#         return app.config.get("PIDSLINK_ENABLED", True)

#     def register(self, pid, record, **kwargs):
#         print(f"[REGISTER] Attempting to register PID: {pid.pid_value}")
#         local_success = super().register(pid)
#         print(f"[REGISTER] super().register(pid) returned: {local_success}")
#         if not local_success:
#             print("[REGISTER] Registration failed at super().register(pid)")
#             return False

#         try:
#             url = f"https://baobabtest.wacren.net/records/{pid.pid_value}"
#             print(f"[REGISTER] Generated URL: {url}", flush=True)
#             print(f"[REGISTER] Calling generate_ark with record: {record}")
#             ark = self.client.generate_ark(record)
#             print(f"[REGISTER] Received ARK: {ark}", flush=True)
#             current_app.logger.info(f"Successfully registered ARK: {ark}")
#             return True
#         except Exception as e:
#             print(f"[REGISTER] Exception occurred: {e}", flush=True)
#             current_app.logger.warning(
#                 f"PIDsLink provider error when registering ARK for {pid.pid_value}"
#             )
#             self._log_errors(e)
#             return False

#     def update(self, pid, record, url, **kwargs):
#         """Update metadata associated with an ARK."""
#         try:
#             self.client.update_ark(pid.pid_value, record, url)
#             return True
#         except PIDsLinkError as e:
#             current_app.logger.warning(
#                 f"PIDsLink provider error when updating ARK for {pid.pid_value}"
#             )
#             self._log_errors(e)
#             return False

