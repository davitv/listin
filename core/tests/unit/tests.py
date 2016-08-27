from __future__ import unicode_literals

import os
from io import BytesIO
from PIL import Image
from decimal import Decimal

import six
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from django.conf import settings

from core.models import Organization, Category
from core.forms import StaffForm
from core.serializers import VacancySerializer, OrganizationSerializer, VisitorMessageSerializer, \
    OrganizationProductSerializer

from jobs.models import Language, Skill


def create_in_memory_test_image():
    file = BytesIO()
    image = Image.new('RGBA', size=(150, 150), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return SimpleUploadedFile(name=file.name, content=file.read())


ORGANIZATION_DATA = dict(
    name="Organization Name",
    inn="12345",
    ogrn="54321",
    url="http://example.com",
    country="RU",
    state="State Moscow",
    city="Moscow",
    address_1="Benjamin str.",
    address_2="home 776",
    email="test@email.com",
    phone="+79261473805",
    description="Description about organization business",
)


class TestStaffForm(TestCase):
    user_cache = None

    def setUp(self):
        self.user_cache = get_user_model()(
            email="some@email.com"
        )
        self.user_cache.set_password("123")
        self.user_cache.save()
        self.factory = RequestFactory()
        business = Organization(
            user=self.user_cache,
            name="Name",
            inn=146465464654,
            ogrn=146465464654,
            address_1="address",
            address_2="address",
            state="State",
            country="ru",
            email="email@domain.com",
            phone="+37494303029",
        )
        business.save()

    def test_staff_correct_data(self):
        request = self.factory.get(reverse("staff-add"))
        request.user = self.user_cache
        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "domain@email.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertTrue(form.is_valid())
        staff = form.save()
        self.assertEqual("First", staff.first_name, )
        self.assertEqual("Last", staff.last_name, )
        self.assertEqual("domain@email.com", staff.email, )
        self.assertEqual("+79261473805", staff.phone, )

    def test_staff_correct_existing_account_data(self):
        request = self.factory.get(reverse("staff-add"))

        existing_user = get_user_model().objects.create_user(
            email="some_other@email.com",
            first_name="Existing First",
            last_name="Existing Last",
        )
        request.user = self.user_cache
        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "some_other@email.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertTrue(form.is_valid())
        staff = form.save()
        self.assertEqual("Existing First", staff.first_name, )
        self.assertEqual("Existing Last", staff.last_name, )
        self.assertEqual("some_other@email.com", staff.email, )
        # phone should be empty because user have not set it up
        self.assertEqual("", staff.phone, )

        self.assertEqual(existing_user, staff.user)

    def test_staff_incorrect_existing_account_data(self):
        request = self.factory.get(reverse("staff-add"))

        # existing user
        get_user_model().objects.create_user(
            email="some_other@email.com",
            first_name="Existing First",
            last_name="Existing Last",
        )
        # other existing user
        get_user_model().objects.create_user(
            email="some_other_mail@email.com",
            first_name="Existing First",
            last_name="Existing Last",
            phone="+79261473805",
        )
        request.user = self.user_cache
        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "some_other@email.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(
            form.error_messages['different_users'] in form.errors['__all__'])

    def test_for_already_invited_exception(self):
        request = self.factory.get(reverse("staff-add"))

        # existing user
        get_user_model().objects.create_user(
            email="davoimail@gmail.com",
            first_name="Existing First",
            last_name="Existing Last",
        )

        # invited first time
        request.user = self.user_cache
        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "davoimail@gmail.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertTrue(form.is_valid(), form.errors.as_text())
        staff = form.save()

        # now will try to do that again with same user

        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "davoimail@gmail.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertFalse(form.is_valid(), form.errors.as_text())
        all_errors = form.errors['__all__']
        self.assertTrue(
            form.error_messages['invite_already_sent'] in all_errors,
            form.errors['__all__'])

        # now let's check exceptin after staff confirms an invite
        staff.is_verified = True
        staff.save()

        form = StaffForm(user=self.user_cache, data={
            "first_name": "First",
            "last_name": "Last",
            "email": "davoimail@gmail.com",
            "phone": "+79261473805",
            "position": "Manager",
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(
            form.error_messages['already_exists'] in form.errors['__all__'],
            form.errors['__all__'])


class TestVacancySerializer(TestCase):
    user_cache = None

    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123'
        )
        self.factory = RequestFactory()
        self.organization_cache = Organization(
            user=self.user_cache,
            name="Name",
            inn=146465464654,
            ogrn=146465464654,
            address_1="address",
            address_2="address",
            state="State",
            country="ru",
            email="email@domain.com",
            phone="+37494303029",
        )
        self.organization_cache.save()
        self.vacancy_data = {
            'organization': str(self.organization_cache.pk),
            'name': "Position Name",
            'description': "Long description goes here...",
            'specialization': 'Engineer',
            'degree': "2",
            'languages': 'English,Russian,German',
            'skills': 'Python,Django,MySQL,Oracle',
            'user': str(self.user_cache.pk),
        }

    def get_vacancy_data(self):
        ret = {}
        ret.update(self.vacancy_data)
        return ret

    def test_correct_input(self):
        data = self.get_vacancy_data()
        serializer = VacancySerializer(data=data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        vacancy = serializer.save()
        self.assertEqual(vacancy.skills.count(), 4)
        self.assertEqual(vacancy.languages.count(), 3)
        self.assertEqual(vacancy.degree, 2)
        self.assertEqual(vacancy.specialization, 'Engineer')

    def test_incorrect_input(self):
        data = self.get_vacancy_data()
        del data['specialization']
        serializer = VacancySerializer(data=data, context={
            'user': self.user_cache
        })
        self.assertFalse(serializer.is_valid())
        self.assertTrue('non_field_errors' in serializer.errors, serializer.errors)
        self.assertEqual('Education value is incomplete',  serializer.errors['non_field_errors'][0],
                         serializer.errors['non_field_errors'][0])

    def test_correct_update(self):
        data = self.get_vacancy_data()
        serializer = VacancySerializer(data=data, context={
            'user': self.user_cache
        })
        serializer.is_valid(True)
        vacancy = serializer.save()
        data['degree'] = '3'
        data['languages'] = 'German,Italian,English'
        data['skills'] = 'Python,Django,NodeJS'
        data['name'] += '_changed'
        update_serializer = VacancySerializer(instance=vacancy, data=data, context={
            'user': self.user_cache
        })
        self.assertTrue(update_serializer.is_valid())
        instance = update_serializer.save()
        self.assertEqual(instance.skills.count(), 3, [s.name for s in instance.skills.all()])
        self.assertEqual(instance.languages.count(), 3)
        self.assertEqual(instance.name, data['name'])

        # check for old values deleted
        self.assertEqual(Language.objects.all().count(), 3)
        self.assertEqual(Skill.objects.all().count(), 3)


class TestTempFileUpload(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123'
        )

    def test_correct_file_upload(self):
        response = self.client.post(reverse('api-tempfile'),
                                    {'file': create_in_memory_test_image()}, HTTP_HOST='example.com')
        self.assertEqual(response.data['count'], 1)
        full_path = os.path.join(settings.FILE_UPLOAD_TEMP_DIR, response.data['results'][0]['name'])
        self.assertTrue(os.path.isfile(full_path), full_path)
        os.remove(full_path)


class TestOrganizationSerializer(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123'
        )
        self.category_cache = Category.objects.create(name="Test Category")
        self.factory = RequestFactory()
        self.test_data = {}
        self.test_data.update(ORGANIZATION_DATA)
        # upload temp image
        response = self.client.post(reverse('api-tempfile'), {'file': create_in_memory_test_image()},
                                    HTTP_HOST='example.com')
        self.temp_image = response.data['results'][0]['name']

    def tearDown(self):
        os.remove(os.path.join(settings.FILE_UPLOAD_TEMP_DIR, self.temp_image))

    def test_correct_create(self):
        self.test_data['category'] = six.text_type(self.category_cache.pk)

        self.test_data['logo_url'] = self.temp_image
        serializer = OrganizationSerializer(data=self.test_data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertTrue(instance.logo is not None)

    def test_correct_update(self):
        self.test_data['category'] = six.text_type(self.category_cache.pk)

        serializer = OrganizationSerializer(data=self.test_data, context={
            'user': self.user_cache
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertFalse(instance.logo)
        self.test_data['logo_url'] = self.temp_image
        serializer = OrganizationSerializer(data=self.test_data, instance=instance, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertTrue(instance.logo)


class TestVisitorMessageSerializer(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123',
            phone='+79261473805',
        )
        self.organization_cache = Organization(
            user=self.user_cache,
            name="Name",
            inn=146465464654,
            ogrn=146465464654,
            address_1="address",
            address_2="address",
            state="State",
            country="ru",
            email="email@domain.com",
            phone="+37494303029",
        )
        self.organization_cache.save()
        self.factory = RequestFactory()
        self.test_data = {
            'email': 'test@email.com',
            'phone': "+79261473805",
            'text': 'Some long smart text goes here',
            'send_to': '1',
            'organization': str(self.organization_cache.pk),

        }

    def test_correct_create(self):
        serializer = VisitorMessageSerializer(data=self.test_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertTrue(instance.phone_status == 0)
        self.assertTrue(instance.email_status == 0)
        self.assertEqual(instance.phone, self.test_data['phone'])
        self.assertEqual(instance.email, self.test_data['email'])
        self.assertEqual(str(instance.send_to), self.test_data['send_to'])

        # now we have an authorized user with unverified phone and email
        serializer = VisitorMessageSerializer(data=self.test_data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertTrue(instance.phone_status == 0)
        self.assertTrue(instance.email_status == 0)
        self.assertEqual(instance.phone, self.test_data['phone'])
        self.assertEqual(instance.email, self.test_data['email'])

        # now we have an authorized user with verified phone and email
        self.user_cache.is_email_confirmed = True
        self.user_cache.is_phone_confirmed = True
        self.user_cache.save()
        serializer = VisitorMessageSerializer(data=self.test_data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertTrue(instance.phone_status == 1)
        self.assertTrue(instance.email_status == 1)
        self.assertEqual(instance.phone, self.test_data['phone'])
        self.assertEqual(instance.email, self.test_data['email'])


class TestOrganizationProductSerializer(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123',
            phone='+79261473805',
        )
        self.organization_cache = Organization(
            user=self.user_cache,
            name="Name",
            inn=146465464654,
            ogrn=146465464654,
            address_1="address",
            address_2="address",
            state="State",
            country="ru",
            email="email@domain.com",
            phone="+37494303029",
        )
        self.category_cache = Category.objects.create(
            name="Category title"
        )

        self.organization_cache.save()
        self.factory = RequestFactory()

    def get_test_data(self):
        return {
            'name': 'Product name',
            'category': str(self.category_cache.pk),
            'description': 'Some long smart text goes here',
            'price': '188.12',
            'quantity': '3',
            'kind': '1',
            'organization': str(self.organization_cache.pk),
            'is_featured': '1',
            'is_popular': '0',
            'image': create_in_memory_test_image()
        }

    def test_correct_create(self):
        data = self.get_test_data()
        serializer = OrganizationProductSerializer(data=data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        inst = serializer.save()

        self.assertEqual(inst.name, data['name'])
        self.assertEqual(inst.price, Decimal(data['price']))
        self.assertEqual(inst.description, data['description'])
        self.assertEqual(inst.quantity, int(data['quantity']))
        organization_product = inst.organizationproduct_set.first()
        self.assertEqual(organization_product.category, self.category_cache)
        self.assertEqual(organization_product.is_featured, data['is_featured'] != '0')
        self.assertEqual(organization_product.is_popular, data['is_popular'] != '0')

    def test_correct_update(self):
        data = self.get_test_data()
        serializer = OrganizationProductSerializer(data=data, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        inst = serializer.save()

        data = self.get_test_data()
        data['name'] = 'Changed product name'
        data['price'] = '43423.123'
        data['is_featured'] = '0'
        data['is_popular'] = '1'
        serializer = OrganizationProductSerializer(data=data, instance=inst, context={
            'user': self.user_cache
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        inst = serializer.save()

        self.assertEqual(inst.name, data['name'])
        self.assertEqual(inst.price, Decimal(data['price']))
        self.assertEqual(inst.description, data['description'])
        self.assertEqual(inst.kind, int(data['kind']))
        self.assertEqual(inst.quantity, int(data['quantity']))
        organization_product = inst.organizationproduct_set.first()
        self.assertEqual(organization_product.category, self.category_cache)
        self.assertEqual(organization_product.is_featured, data['is_featured'] != '0')
        self.assertEqual(organization_product.is_popular, data['is_popular'] != '0')


class TestOrganizationProductAPIView(TestCase):
    def setUp(self):
        self.user_cache = get_user_model().objects.create_user(
            email="test@email.com",
            password='123',
            phone='+79261473805',
        )
        self.organization_cache = Organization(
            user=self.user_cache,
            name="Name",
            inn=146465464654,
            ogrn=146465464654,
            address_1="address",
            address_2="address",
            state="State",
            country="ru",
            email="email@domain.com",
            phone="+37494303029",
        )
        self.category_cache = Category.objects.create(
            name="Category title"
        )

        self.organization_cache.save()
        self.factory = RequestFactory()
        self.client = Client(HTTP_HOST='example.com')
        self.client.login(username=self.user_cache.email, password='123')

    def get_test_data(self):
        return {
            'name': 'Product name',
            'category': str(self.category_cache.pk),
            'description': 'Some long smart text goes here',
            'price': '188.12',
            'quantity': '3',
            'kind': '1',
            'organization': str(self.organization_cache.pk),
            'is_featured': '1',
            'is_popular': '0',
            'image': create_in_memory_test_image()
        }

    def test_correct_create(self):
        data = self.get_test_data()
        response = self.client.post(reverse('api-products-list'), data=data)
        response.render()
