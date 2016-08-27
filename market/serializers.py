from __future__ import unicode_literals

from rest_framework import serializers

from .models import Product
from .models import Attribute
from .models import AttributeValue


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = (
            'user',
        )

    def save(self, **kwargs):
        if 'user' not in self.context:
            raise Exception
        return super(ProductSerializer, self).save(user=self.context['user'])
