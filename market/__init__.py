from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_product_model():
    """
    Returns the Product model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.MARKET_PROUCT_MODEL)
    except ValueError:
        raise ImproperlyConfigured("MARKET_PRODUCT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "MARKET_PRODUCT_MODEL refers to model '%s' that has not been installed" % settings.MARKET_PRODUCT_MODEL
        )