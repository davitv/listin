# coding=utf-8
from __future__ import unicode_literals
import os
import random
from chance import chance
from django.core.management.base import BaseCommand
from listin.models import Organization, OrganizationProduct, Branch
from listin.models import Staff
from listin.models import Product
from listin.models import Category
from profiles.models import User
from django.core.files import File


class Command(BaseCommand):
    help = 'Generates organizations for testing purposes'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []
    categories_list = []

    def add_arguments(self, parser):
        parser.add_argument('amount', type=int)
        parser.add_argument('images_path', type=str)

    def create_user(self):
        user = User(
            first_name=chance.first(gender='m', language='ru'),
            last_name=chance.last(gender='m', language='ru'),
            email=chance.email(),
            is_active=True,
            is_email_confirmed=True,
        )
        user.set_password("@120804a")
        user.save()
        self.stdout.write('Successfully created user (%s)' % (user.email, ))
        return user

    def create_staff(self, business):
        staff = Staff(
            user=self.create_user(),
            organization=business,
            position=chance.word(language='ru')
        )
        staff.save()
        self.stdout.write('Successfully created staff (%s)' %
                          (staff.email, ))
        return staff

    def create_product(self, business, user):
        images_path = self.images_dir + self.images_dir_list[random.randint(0, len(self.images_dir_list)-1)]
        product = Product(
            name=chance.sentence(language='ru', words=4),
            price=random.randint(10000, 123456),
            description=chance.paragraph(sentences=5),
            user=user,

        )
        with open(images_path, 'r') as f:
            image_file = File(f)
            product.image.save('picture.' + images_path.split('.')[-1:][0], image_file, True)
        product.save()

        organization_product = OrganizationProduct(
            product=product,
            is_featured=chance.boolean(),
            is_popular=chance.boolean(),
            is_service=chance.boolean(),
            organization=business,
        )
        organization_product.save()
        self.stdout.write('Successfully created product (%s)' % (product.name, ))
        return product

    def create_organization(self):
        images_path = self.images_dir + self.images_dir_list[random.randint(0, len(self.images_dir_list)-1)]

        inn = random.randint(10000000, 9999999999)
        ogrn = random.randint(10000000, 9999999999)
        user = self.create_user()

        category = None
        if self.categories_list:
            category = random.choice(self.categories_list)
        organization = Organization(
            user=user,
            name=chance.sentence(3),
            inn=inn,
            ogrn=ogrn,
            country="RU",
            address_1=chance.street(language='ru'),
            address_2=chance.street(language='ru'),
            state=chance.state(language='ru'),
            email=chance.email(),
            phone=chance.phone(),
            description=chance.paragraph(language='ru'),
            url=chance.url(),
            is_confirmed=True,
            category=category,
        )
        with open(images_path, 'r') as f:
            image_file = File(f)
            organization.image.save('picture.' + images_path.split('.')[-1:][0], image_file, True)

        organization.save()

        for x in range(0, 15):
            self.create_staff(organization)
            self.create_product(organization, user)
        for x in range(0, random.randint(1, 8)):
            self.create_branch(organization)
        return organization

    def create_branch(self, organization):
        branch = Branch.objects.create(
            name=chance.sentence(3),
            organization=organization,
            country="RU",
            address_1=chance.street(language='ru'),
            address_2=chance.street(language='ru'),
            state=chance.state(language='ru'),
            email=chance.email(),
            phone=chance.phone(),
            description=chance.paragraph(language='ru'),
        )
        return branch

    def handle(self, *args, **options):
        self.images_dir_list = os.listdir(options['images_path'])
        self.images_dir = options['images_path']
        self.categories_list = Category.objects.all()
        for x in range(0, options['amount']):
            b = self.create_organization()
            self.stdout.write(self.style.SUCCESS(u'Successfully created business %s (%s)' %
                                                 (b.name, b.address_1)))
