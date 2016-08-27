import os

from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from rest_framework import serializers


def get_file_by_url(value):
    validator = URLValidator('')
    try:
        validator(value)
    except ValidationError:
        return False
    else:
        return True


def get_file_by_path(value):
    try:
        file = open(os.path.join(settings.FILE_UPLOAD_TEMP_DIR, value))
    except IOError:
        return False
    else:
        return file


def validate_file_url(value):
    file_instance = get_file_by_path(value) or get_file_by_url(value)
    if not file_instance:
        raise serializers.ValidationError('This field must be a correct path to an existing temp file.')
    return file_instance

