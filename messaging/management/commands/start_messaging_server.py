# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from business.models import Category
from django.conf import settings
from messaging.views import start_messaging_server



class Command(BaseCommand):
    help = 'Dumps categories as JSON tree'
    images_dir_list = []
    images_dir = ''
    products_images_dir_list = []

    def handle(self, *args, **options):
        start_messaging_server(settings.WEBSOCKET_PORT,
                               settings.WEBSOCKET_ALLOWED_ORIGINS,
                               settings.REDIS_HOST,
                               settings.REDIS_PORT,)
