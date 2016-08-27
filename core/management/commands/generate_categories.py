# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
import random
from chance import chance
from listin.models import Category
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Generates categories for testing purposes'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []

    def add_arguments(self, parser):
        parser.add_argument('amount', type=int)
        parser.add_argument('depth', type=int)
        parser.add_argument('images_path', type=str)

    def create_category(self, parent=None):
        images_path = self.images_dir + self.images_dir_list[random.randint(0, len(self.images_dir_list) - 1)]
        category = Category(
            name=chance.word(3, language='ru'),
            description=chance.sentence(3, language='ru'),
            parent=parent
        )
        with open(images_path, 'r') as f:
            image_file = File(f)
            category.icon.save('picture.jpg', image_file, True)

        category.save()

        return category

    def handle(self, *args, **options):
        self.images_dir_list = os.listdir(options['images_path'])
        self.images_dir = options['images_path']
        depth = options['depth']

        def create_children(category, depth):
            for x in range(0, options['amount']):
                c = self.create_category(category)
                if depth - 1 > 0:
                    create_children(c, depth - 1)

        for x in range(0, options['amount']):
            c = self.create_category()
            if depth != 0:
                create_children(c, depth)
            self.stdout.write(self.style.SUCCESS(u'Successfully created category %s' %
                                                 (c.name,)))
