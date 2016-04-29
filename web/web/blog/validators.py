"""Custom Form Field validators in ModelForms."""
from django.core.exceptions import ValidationError


def validate_title(value):
    """Raise a ValidationError if the value doesn't start with 'Django'."""
    if not value.startswith(u"Django"):
        msg = u"Must start with Django"
        raise ValidationError(msg, code="invaild")
