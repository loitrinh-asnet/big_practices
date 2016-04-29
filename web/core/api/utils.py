"""Utils."""
import re

MINIMUM_PASSWORD_LENGTH = 6
REGEX_VALID_PASSWORD = (
    # Don't allow any spaces (\t, \n or whitespace)
    r'^(?!.*[\s])'
)


def minimum_password_length():
    """Minimum password length."""
    return MINIMUM_PASSWORD_LENGTH


def validate_password(password):
    """Password validation."""
    if re.match(REGEX_VALID_PASSWORD, password):
        return True
    return False
