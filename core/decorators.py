from __future__ import unicode_literals
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from .models import Organization, BusinessException


def company_required(function=None, business_add_url=None):
    def test_func(u):
        try:
            assert u.is_authenticated()
            Organization.objects.get_company(u)
        except (AssertionError, BusinessException, ObjectDoesNotExist,):
            # user have no his own company,
            # lets see if he is a staff somewhere
            organizations = Organization.objects.get_user_related_companies(u)
            if organizations.count():
                return True
            return False
        return True

    actual_decorator = user_passes_test(
        test_func,
        login_url=business_add_url,
    )

    if function:
        return actual_decorator(function)
    return actual_decorator
