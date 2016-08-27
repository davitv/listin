from __future__ import unicode_literals

from rest_framework import serializers

from .models import CV


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        exclude = (
            'user',
        )
