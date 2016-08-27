"""
This module contains views that are related to non-authorized
users (visitors) views.
"""
from __future__ import unicode_literals
import sys
import redis
import six
import logging
from tornado import web, ioloop, websocket
from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import MiddlewareNotUsed

logger = logging.getLogger('django.request')


class BaseDjangoWebSocketHandler(websocket.WebSocketHandler):
    """
    This websocket handler is maintaining users authentication
    by applying some of django's middleware and saves them to
    redis as a hashmap.
    """
    allowed_origins = []
    redis_client = None

    def initialize(self, on_message, on_open, on_close, allowed_origins):
        self._on_message = on_message
        self._open = on_open
        self._on_close = on_close
        self.allowed_origins = allowed_origins

    def check_origin(self, origin):
        return origin in self.allowed_origins

    def open(self, *args, **kwargs):
        self._open(self)

    def on_message(self, message):
        self._on_message(self, message)

    def on_close(self):
        self._on_close(self)
        print("WebSocket closed")


def get_redis_connection(host, port):
    return redis.StrictRedis(host=host, port=port, db=0)


class WebSocketServer(object):
    allowed_origins = []
    redis_client = None
    tornado_app = None
    connections = []

    _response_middleware = []
    _request_middleware = []

    def __init__(self, port, allowed_origins, redis_host, redis_port):
        self.redis_client = get_redis_connection(redis_host, redis_port)
        self.port = port
        self.tornado_app = web.Application([
            ('/websocket', BaseDjangoWebSocketHandler, dict(
                on_message=self.on_message,
                on_open=self.on_open,
                on_close=self.on_close,
                allowed_origins=allowed_origins,
            ),),
        ])
        self.load_middleware()

    def listen(self):
        self.tornado_app.listen(self.port)
        sys.stdout.write("Starting tornado server at port %s\n" % (self.port, ))
        ioloop.IOLoop.instance().start()

    def load_middleware(self):
        """
        Populate middleware lists from settings.WEBSOCKET_MIDDLEWARE_CLASSES.
        """
        self._response_middleware = []
        request_middleware = []

        for middleware_path in settings.WEBSOCKET_MIDDLEWARE_CLASSES:
            mw_class = import_string(middleware_path)
            try:
                mw_instance = mw_class()
            except MiddlewareNotUsed as exc:
                if settings.DEBUG:
                    if six.text_type(exc):
                        logger.debug('MiddlewareNotUsed(%r): %s', middleware_path, exc)
                    else:
                        logger.debug('MiddlewareNotUsed: %r', middleware_path)
                continue

            if hasattr(mw_instance, 'process_request'):
                request_middleware.append(mw_instance.process_request)
            if hasattr(mw_instance, 'process_response'):
                self._response_middleware.insert(0, mw_instance.process_response)

        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._request_middleware = request_middleware

    def on_open(self, connection, *args, **kwargs):
        response = None
        request = connection.request

        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response:
            # TODO: handle middleware response
            pass

        self.connections.append({
            'user': request.user,
            'connection': connection,
        })
        print len(self.connections)
        import pdb
        pdb.set_trace()

    def on_message(self, connection, message):
        pass

    def on_close(self, connection):
        self.remove_user_connection(connection)
        print len(self.connections)

    def remove_user_connection(self, connection):
        index = -1
        for i, c in enumerate(self.connections):
            if c['connection'] == connection:
                index = i
                break
        if index >= 0:
            self.connections.pop(index)


def start_messaging_server(port, allowed_origins, redis_host, redis_port):
    socket_server = WebSocketServer(port, allowed_origins, redis_host, redis_port)
    socket_server.listen()


