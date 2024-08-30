# -*- coding: utf-8 -*-
#
# This file is part of PIDsLink integration.
#
# PIDsLink integration is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Errors for the PIDsLink API.

PIDsLink error responses will be converted into an exception from this module.
Connection issues raises :py:exc:`PIDsLink.errors.HttpError` while PIDsLink
error responses raise a subclass of
:py:exc:`pidslink.errors.PIDsLinkError`.
"""


class HttpError(Exception):
    """Exception raised when a connection problem happens."""


class PIDsLinkError(Exception):
    """Exception raised when the server returns a known HTTP error code.

    Known HTTP error codes include:

    * 204 No Content
    * 400 Bad Request
    * 401 Unauthorized
    * 403 Forbidden
    * 404 Not Found
    * 410 Gone (deleted)
    """

    @staticmethod
    def factory(err_code, *args):
        """Create exceptions through a Factory based on the HTTP error code."""
        if err_code == 204:
            return PIDsLinkNoContentError(*args)
        elif err_code == 400:
            return PIDsLinkBadRequestError(*args)
        elif err_code == 401:
            return PIDsLinkUnauthorizedError(*args)
        elif err_code == 403:
            return PIDsLinkForbiddenError(*args)
        elif err_code == 404:
            return PIDsLinkNotFoundError(*args)
        elif err_code == 410:
            return PIDsLinkGoneError(*args)
        elif err_code == 412:
            return PIDsLinkPreconditionError(*args)
        else:
            return PIDsLinkServerError(*args)


class PIDsLinkServerError(PIDsLinkError):
    """An internal server error happened on the PIDsLink end. Try later.

    Base class for all 5XX-related HTTP error codes.
    """


class PIDsLinkRequestError(PIDsLinkError):
    """An PIDsLink request error. You made an invalid request.

    Base class for all 4XX-related HTTP error codes as well as 204.
    """


class PIDsLinkNoContentError(PIDsLinkRequestError):
    """PIDsLink identifier is known to the system, but not resolvable.

    This might be due to handle's latency.
    """


class PIDsLinkBadRequestError(PIDsLinkRequestError):
    """Bad request error.

    Bad requests can include e.g. invalid XML, wrong domain, wrong prefix.
    Request body must be correctly formatted for PIDsLink requests.
    """

class PIDsLinkNotFoundError(PIDsLinkRequestError):
    """PIDsLink identifier does not exist in the database."""


class PIDsLinkGoneError(PIDsLinkRequestError):
    """Requested identifier was marked inactive (using DELETE method)."""


class PIDsLinkPreconditionError(PIDsLinkRequestError):
    """Metadata must be uploaded first before performing this operation."""
