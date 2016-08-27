# coding=utf-8
from django.core.management.base import BaseCommand
import random
from chance import chance
from business.models import Category
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Read categories from Areg'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('images_path', type=str)

    def create_category(self, name, parent=None):
        images_path = self.images_dir + self.images_dir_list[random.randint(0, len(self.images_dir_list)-1)]
        category = Category(
            name=name,
            parent=parent
        )
        with open(images_path, 'r') as f:
            image_file = File(f)
            category.icon.save('picture.png', image_file, True)

        category.save()

        return category

    def handle(self, *args, **options):
        self.images_dir_list = os.listdir(options['images_path'])
        self.images_dir = options['images_path']
        file_path = options['file_path']
        text = file(file_path, 'r').read()
        text = text.decode("utf-8")
        blocks = text.split(u"-:-:-")
        for block in blocks:
            category_names = [x for x in block.split("\n") if len(x.strip())]
            parent = None
            for i, name in enumerate(category_names):

                c = self.create_category(name, parent)
                if i == 0:
                    parent = c

                self.stdout.write(self.style.SUCCESS(u'Successfully created category %s' %
                                                 (c.name,)))

