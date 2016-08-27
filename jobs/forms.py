from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import Widget

from jobs.models import CV, Education, Skill, Language, Experience


class FormSetWidget(Widget):
    def render(self, name, value, attrs=None):
        pass

    MIN_NUM = 0
    MAX_NUM = 40

    def value_from_datadict(self, data, files, name):
        """
        This method returns constructed form instances
        list with populated fields from data.
        """
        form_class = self.attrs['form_class']
        form = form_class()
        field_items = [(n, field,) for n, field in form.fields.items() if not field.disabled]
        forms_list = list()
        for x in range(self.MIN_NUM, self.MAX_NUM):
            pk = data.get("%s-%s-pk" % (name, x,), None)

            form_kwargs = dict(
                instance=None,
                data={}
            )
            for k, v in field_items:
                value = data.get("%s-%s-%s" % (name, x, k,), None)
                if value:
                    form_kwargs['data'][k] = value

            if not form_kwargs['data']:
                del form_kwargs['data']

            delete = data.get("%s-%s-DELETE" % (name, x,), False)
            if pk:
                try:
                    form_kwargs['instance'] = form._meta.model.objects.get(pk=pk)
                except ObjectDoesNotExist:
                    pass

            if form_kwargs.get('data') or delete:
                # TODO: try to use only one instance of form
                form = form_class(**form_kwargs)
                form._related_name = name
                form._delete = delete
                forms_list.append(form)
            else:
                break
        return forms_list


class RelatedFormField(forms.Field):

    def __init__(self, *args, **kwargs):
        super(RelatedFormField, self).__init__(*args, **kwargs)

    def validate(self, value):
        "Check if value consists only of valid forms."
        errors = list()
        for i, form in enumerate(value):
            try:
                assert form.is_valid()
            except AssertionError:
                for k, v in form.errors.items():
                    errors.append(
                        ("%s-%s-%s" % (form._related_name, k, i, ), v.as_text())
                    )
        if errors:
            raise forms.ValidationError(errors)


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ("cv", )


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        exclude = ("cv",)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ("cv",)


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ("cv",)


class CVForm(forms.ModelForm):
    education = RelatedFormField(required=False, widget=FormSetWidget(attrs={
        'form_class': EducationForm
    }))

    skill = RelatedFormField(required=False, widget=FormSetWidget(attrs={
        'form_class': SkillForm,
    }))

    experience = RelatedFormField(required=False, widget=FormSetWidget(attrs={
        'form_class': ExperienceForm
    }))

    language = RelatedFormField(required=False, widget=FormSetWidget(attrs={
        'form_class': LanguageForm
    }))

    def clean(self):
        data = self.cleaned_data
        return data

    def process_foreign_forms(self, instance):
        for k, v in self.fields.items():
            if type(v) == RelatedFormField and self.cleaned_data.get(k):
                for form in self.cleaned_data.get(k):
                    if form._delete:
                        if form.instance.pk:
                            form.instance.delete()
                        continue
                    form_instance = form.instance
                    form_instance.cv = instance
                    form_instance.save()
        return None

    def save(self, commit=True):
        instance = super(CVForm, self).save(commit=False)
        instance.user = self.initial['user']
        if commit:
            instance.save()
            self.process_foreign_forms(instance)

        return instance

    class Meta:
        model = CV
        exclude = ('user', )
