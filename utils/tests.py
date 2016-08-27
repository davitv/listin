from __future__ import unicode_literals
import unittest

from django import forms

from .forms import form_to_dict


class ExampleForm(forms.Form):
    CHOICES = (
        (1, 'One',),
        (2, 'Two',),
        (3, 'Three',),
    )
    chars = forms.CharField(required=True)
    chars2 = forms.CharField(required=False)
    text = forms.CharField(required=True)
    text2 = forms.CharField(required=False)
    select = forms.ChoiceField(required=True, choices=CHOICES)
    select2 = forms.ChoiceField(required=False, choices=CHOICES)
    boolean = forms.BooleanField(required=True)
    boolean2 = forms.BooleanField(required=False)
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(required=False)
    date = forms.DateField(required=True, input_formats=['%Y-%m-%d', '%m/%d/%y'])
    date2 = forms.DateField(required=False, input_formats=['%Y-%m-%d', '%m/%d/%y'])
    datetime = forms.DateTimeField(required=True, input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'])
    decimal = forms.DecimalField(required=True)
    duration = forms.DurationField(required=True)
    file = forms.FileField(required=True)
    filepath = forms.FilePathField(path='some/path', required=True)

EXPECTED_RETURN_DICT = {
    'chars': {
        'type': 'CharField',
        'value': '',
        'name': 'chars',
        'required': True
    },
    'chars2': {
        'type': 'CharField',
        'value': '',
        'name': 'chars2',
        'required': False
    },
    'text': {
        'type': 'CharField',
        'value': '',
        'name': 'text',
        'required': True
    },
    'text2': {
        'type': 'CharField',
        'value': '',
        'name': 'text2',
        'required': False
    },
    'select': {
        'type': 'ChoiceField',
        'value': '',
        'name': 'select',
        'required': True,
        'choices': ExampleForm.CHOICES
    },
    'select2': {
        'type': 'ChoiceField',
        'value': '',
        'name': 'select2',
        'required': False,
        'choices': ExampleForm.CHOICES
    },
    'boolean': {
        'type': 'BooleanField',
        'value': '',
        'name': 'boolean',
        'required': True
    },
    'boolean2': {
        'type': 'BooleanField',
        'value': '',
        'name': 'boolean2',
        'required': False
    },
    'email': {
        'type': 'EmailField',
        'value': '',
        'name': 'email',
        'required': True
    },
    'email2': {
        'type': 'EmailField',
        'value': '',
        'name': 'email2',
        'required': False
    },
    'date': {
        'type': 'DateField',
        'value': '',
        'name': 'date',
        'required': True,
        'input_formats': [
            '%Y-%m-%d',
            '%m/%d/%y',
        ]
    },
    'date2': {
        'type': 'DateField',
        'value': '',
        'name': 'date2',
        'required': False,
        'input_formats': [
            '%Y-%m-%d',
            '%m/%d/%y',
        ]
    },
    'datetime': {
        'type': 'DateTimeField',
        'value': '',
        'name': 'datetime',
        'required': True,
        'input_formats': [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M'
        ]
    },
    'decimal': {
        'type': 'DecimalField',
        'value': '',
        'name': 'decimal',
        'required': True
    },
    'duration': {
        'type': 'DurationField',
        'value': '',
        'name': 'duration',
        'required': True
    },
    'file': {
        'type': 'FileField',
        'value': '',
        'name': 'file',
        'required': True
    },
    'filepath': {
        'type': 'FilePathField',
        'value': '',
        'name': 'filepath',
        'required': True
    },
}


# class TestFormToDictFunc(unittest.TestCase):
#     def setUp(self):
#         self.form_bound = ExampleForm({})
#         self.form = ExampleForm()
#         self.maxDiff = None
#
#     def test_correct_return_value(self):
#
#         self.assertDictEqual(form_to_dict(ExampleForm()), EXPECTED_RETURN_DICT)
#
# if __name__ == '__main__':
#     unittest.main()
