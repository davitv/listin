# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from business.models import Category
from django.core import serializers


class Command(BaseCommand):
    help = 'Dumps categories as JSON tree'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []

    def add_arguments(self, parser):
        parser.add_argument('save_path', type=str)

    def handle(self, *args, **options):
        with open(options['save_path'], 'w') as outfile:
            serializers.serialize("json", Category.objects.all(), stream=outfile)
        self.stdout.write(self.style.SUCCESS(u'Successfully dumped categories tree to %s' %
                                             (options['save_path'],)))
