from django.views import generic
from django.forms import inlineformset_factory
from .forms import CVForm
from .models import CV, Education


class CVFormView(generic.FormView):
    form_class = CVForm

    def get_context_data(self, **kwargs):
        context = super(CVFormView, self).get_context_data(**kwargs)

        return context