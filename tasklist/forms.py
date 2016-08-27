from __future__ import unicode_literals

from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = (
            "added_by",
        )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(TaskForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        task = super(TaskForm, self).save(False)
        task.added_by = self.request.user
        if commit:
            task.save()
        return task
