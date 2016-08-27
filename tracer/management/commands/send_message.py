from __future__ import unicode_literals

from optparse import make_option
from django.core.management import BaseCommand
import zmq


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
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('tcp://127.0.0.1:8882')
        self.socket.send_json({
            'data': {
                'refresh': 'page'
            },
            'query': {
                'room': 'admin'
            }
        })
