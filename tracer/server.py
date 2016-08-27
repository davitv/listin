from __future__ import unicode_literals
import logging

from tornado import web
from tracer.zmq_connection import ZMQClientThread
import simplejson as json

logger = logging.getLogger('django.request')


class TracerSocketServer(web.Application):
    active_connections = {}
    redis_connection = None

    def __init__(self, *args, **kwargs):
        super(TracerSocketServer, self).__init__(*args, **kwargs)
        self.zmq_client = ZMQClientThread(self._on_zmq_message_received)
        self.zmq_client.daemon = True
        self.zmq_client.start()

    def _on_zmq_message_received(self, message):
        message = json.loads(message)
        self.send_message(message['data'], **message['query'])

    def add_connection(self, conn):
        self.active_connections[id(conn)] = conn
        sessions = set([c.info['session'] for key, c in self.active_connections.items()])
        self.send_message({
            'active_connections_count': len(self.active_connections),
            'unique_connections_count': len(sessions)
        }, room='admin')

    def open(self, conn):
        self.add_connection(conn)

    def send_message(self, data, **kwargs):
        connections = self.search_connections(**kwargs)
        if connections:
            for conn in connections:
                conn.write_message(data)
        return len(connections)

    def on_close(self, conn):
        del self.active_connections[id(conn)]
        sessions = set([c.info['session'] for key, c in self.active_connections.items()])
        self.send_message({
            'active_connections_count': len(self.active_connections),
            'unique_connections_count': len(sessions)
        }, room='admin')

    def on_message(self, conn, message):
        action = message.get('action')
        if action == 'subscribe':
            room = message.get('room')
            conn.info['rooms'].append(room)
            sessions = set([c.info['session'] for key, c in self.active_connections.items()])
            self.send_message({
                'active_connections_count': len(self.active_connections),
                'unique_connections_count': len(sessions)
            }, room='admin')

    def search_connections(self, room=None, uids=None):
        ret = []
        if room is not None:
            for key, conn in self.active_connections.items():
                if room in conn.info['rooms']:
                    ret.append(conn)
        if uids is not None:
            for key, conn in self.active_connections.items():
                if conn.info['user'] in uids:
                    ret.append(conn)
        return ret
