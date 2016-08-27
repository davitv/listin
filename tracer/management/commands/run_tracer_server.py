from __future__ import unicode_literals

import sys

from optparse import make_option
from tornado import ioloop
from django.core.management import BaseCommand
from django.utils.module_loading import import_string
from tracer.server import TracerSocketServer


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--port',
            default='8888',
            dest='port',
            help='Specifies the websocket server port',
        ),
        make_option(
            '--handler',
            default='tracer.views.DefaultTracerWebsocketHandler',
            dest='handler',
            help='Specifies the websocket server handler',
        ),
    )

    help = "Run tornado websocket server"

    def handle(self, **options):
        port = options.get('port')
        handler_import_path = options.get('handler')
        handler_class = import_string(handler_import_path)

        tornado_app = TracerSocketServer([
            ('/websocket', handler_class, ),
        ])

        tornado_app.listen(int(port))
        sys.stdout.write("Starting tornado server at port %s\n" % (port,))
        ioloop.IOLoop.instance().start()
