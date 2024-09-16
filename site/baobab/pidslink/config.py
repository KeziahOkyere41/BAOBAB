# ARK configuration settings
PIDSLINK_ENABLED = True
"""Flag to enable/disable ARK registration."""

PIDSLINK_USERNAME = ""
"""PIDsLink username."""

PIDSLINK_PASSWORD = ""
"""PIDsLink password."""

PIDSLINK_PREFIX = "50962/bb67854"
"""PIDsLink prefix."""

PIDSLINK_TEST_MODE = False
"""PIDsLink test mode enabled."""

PIDSLINK_FORMAT = "ark:/50962/bb67854/{identifier}"
"""A string used for formatting the ARK or a callable.

print(f"PIDSLINK_FORMAT: {PIDSLINK_FORMAT}")