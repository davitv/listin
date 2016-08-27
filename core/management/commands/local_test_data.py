# coding=utf-8
from __future__ import unicode_literals
import random
from chance import chance
from django.core.management.base import BaseCommand
from listin.models import Organization
from profiles.models import User


class Command(BaseCommand):
    help = 'Creates local account for Davit :)'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []

    def create_user(self):
        user = User(
            first_name="Davit",
            last_name="Vardanyan",
            email="davoimail@gmail.com",
            is_active=True,
            is_email_confirmed=True,
            is_superuser=True,
            is_staff=True,
        )
        user.set_password("@120804a")
        user.save()
        self.stdout.write('Successfully created user (%s)' % (user.email, ))
        return user

    def create_business(self):
        user = self.create_user()
        business = Organization(
            user=user,
            name=chance.sentence(3),
            inn=random.randint(10000000, 9999999999),
            ogrn=random.randint(10000000, 9999999999),
            country="RU",
            address_1=chance.street(language='ru'),
            address_2=chance.street(language='ru'),
            state=chance.state(language='ru'),
            email=chance.email(),
            phone=chance.phone(),
            description=chance.paragraph(language='ru'),
            url=chance.url(),
            is_confirmed=True,
        )
        business.save()
        return business

    def handle(self, *args, **options):
        b = self.create_business()
        self.stdout.write(self.style.SUCCESS(u'Successfully created business %s (%s)' %
                                             (b.name, b.address_1)))

