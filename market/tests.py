from __future__ import unicode_literals

from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth import get_user_model

from .serializers import ProductSerializer

from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal


def create_in_memory_test_image():
    file = BytesIO()
    image = Image.new('RGBA', size=(150, 150), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return SimpleUploadedFile(name=file.name, content=file.read())


class TestOrganizationProductSerializer(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123',
            phone='+79261473805',
        )
        self.factory = RequestFactory()
        self.test_data = {
            'name': 'Product name',
            'description': 'Some long smart text goes here',
            'price': '188.12',
            'quantity': '3',
            'kind': '1',
            'image': create_in_memory_test_image()
        }

    def test_correct_create(self):
        data = self.test_data
        serializer = ProductSerializer(data=self.test_data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        inst = serializer.save()

        self.assertEqual(inst.user, self.user_cache)
        self.assertEqual(inst.name, data['name'])
        self.assertEqual(inst.price, Decimal(data['price']))
        self.assertEqual(inst.description, data['description'])
        self.assertEqual(inst.quantity, int(data['quantity']))
        self.assertTrue(inst.image)
