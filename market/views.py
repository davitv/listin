from __future__ import unicode_literals

from django.views import generic


class HomePageView(generic.TemplateView):
    template_name = 'market/index.html'
