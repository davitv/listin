from django import forms

from .models import (
    Product, Attribute, AttributeValue,
)


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
