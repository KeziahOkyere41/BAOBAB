# ARK configuration settings
PIDSLINK_ENABLED = False
"""Flag to enable/disable ARK registration."""

PIDSLINK_USERNAME = ""
"""PIDsLink username."""

PIDSLINK_PASSWORD = ""
"""PIDsLink password."""

PIDSLINK_PREFIX = ""
"""PIDsLink prefix."""

PIDSLINK_TEST_MODE = True
"""PIDsLink test mode enabled."""

PIDSLINK_FORMAT = "ark:/${prefix}/${value}"
"""A string used for formatting the ARK or a callable.
