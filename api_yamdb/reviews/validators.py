from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            _('Недопустимое значение: %(value)s'),
            params={'value': value},
        )
