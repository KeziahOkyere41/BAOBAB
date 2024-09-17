# ARK configuration settings#
from baobab.pidslink.provider.pidslink import PIDsLinkClient

PIDSLINK_ENABLED = True
"""Flag to enable/disable ARK registration."""

PIDSLINK_USERNAME = ""
"""PIDsLink username."""

PIDSLINK_PASSWORD = ""
"""PIDsLink password."""

PIDSLINK_PREFIX = "50962/bb67854"
"""PIDsLink prefix."""

PIDSLINK_TEST_MODE = True
"""PIDsLink test mode enabled."""

PIDSLINK_FORMAT = ark_format"{record.pid.pid_value}"
"""A string used for formatting the ARK or a callable.

print(f"PIDSLINK_FORMAT: {PIDSLINK_FORMAT}")