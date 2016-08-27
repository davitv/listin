"""
This module contains views that are related to non-authorized
users (visitors) views.
"""
from django.views import generic
from core.serializers import CategorySerializer
from twilio.util import TwilioCapability

from core.models import (
    Organization, Category, OrganizationProduct,
    Staff,
)

from django.conf import settings


class TwillioView(generic.TemplateView):
    template_name = 'twillio.html'

    def get_context_data(self, **kwargs):
        context = super(TwillioView, self).get_context_data(**kwargs)
        context['account_sid'] = settings.TWILLIO_ACCOUNT_SID
        context['auth_token'] = settings.TWILLIO_AUTH_TOKEN
        context['auth_token'] = settings.TWILLIO_APP_SID
        capability = TwilioCapability(settings.TWILLIO_ACCOUNT_SID, settings.TWILLIO_AUTH_TOKEN)
        capability.allow_client_outgoing(settings.TWILLIO_APP_SID)
        context['token'] = capability.generate()
        return context


class HomePageView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['organizations'] = Organization.objects.filter(branch__isnull=True)
        import json
        context['categories_json_tree'] = json.dumps(Category.objects.get_serialized_tree(CategorySerializer))
        return context


class OrganizationVacanciesPage(generic.DetailView):
    template_name = 'vacancy-list.html'
    queryset = Organization.objects.all()

    def get_context_data(self, **kwargs):
        context = super(OrganizationVacanciesPage, self).get_context_data(**kwargs)
        organization = self.object
        context['organization'] = organization
        context['vacancies'] = organization.vacancies.all()
        return context


class SocialAuthSuccess(generic.RedirectView):
    url = None


class OrganizationViewPage(generic.DetailView):
    template_name = 'organization.html'
    queryset = Organization.objects.all()

    def get_context_data(self, **kwargs):
        context = super(OrganizationViewPage, self).get_context_data(**kwargs)
        organization = self.object
        products = OrganizationProduct.objects.filter(organization=organization).order_by('id')
        context['products'] = products.filter(product__kind=0).order_by('id')
        context['services'] = products.filter(product__kind=1).order_by('id')
        context['projects'] = products.filter(product__kind=2).order_by('id')
        context['business'] = organization

        context['admin'] = context['company_admin'] = self.request.user.is_authenticated() and self.object.user == self.request.user

        context['featured_products'] = products.filter(is_featured=True)
        context['popular_products'] = products.filter(is_popular=True)
        context['staff'] = Staff.objects.filter(organization=organization)

        return context
