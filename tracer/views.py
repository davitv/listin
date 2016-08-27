from __future__ import unicode_literals
import uuid
from django.views import generic


class HomePageView(generic.TemplateView):
    template_name = 'tracer/base.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        self.request.session['uuid'] = str(uuid.uuid1())
        return context