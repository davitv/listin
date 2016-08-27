from __future__ import unicode_literals

from tornado.websocket import WebSocketHandler

from django.core.exceptions import MiddlewareNotUsed
from django.utils.module_loading import import_string
from django.conf import settings

import six
import logging
import simplejson as json

logger = logging.getLogger('django.request')


try:
    from urllib.parse import urlparse  # py2
except ImportError:
    from urlparse import urlparse  # py3


class TracerWebsocketHandler(WebSocketHandler):

    _response_middleware = None

    def __init__(self, *args, **kwargs):
        super(TracerWebsocketHandler, self).__init__(*args, **kwargs)
        self.application.active_connections[id(self)] = self
        self.load_middleware()
        self.info = {
            'rooms': [],
            'user': 0
        }

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

    def on_connection_close(self):
        super(TracerWebsocketHandler, self).on_connection_close()
        self.application.on_close(self)

    def open(self):
        response = None
        request = self.request

        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                break
        if response:
            # TODO: handle middleware response
            pass
        self.info['user'] = request.user.pk if request.user.is_authenticated() else 0
        if getattr(request, 'session', False):
            self.info['session'] = request.session.session_key
        self.application.open(self)

    def on_message(self, message):
        self.application.on_message(self, json.loads(message))

    def on_close(self):
        pass

    def check_origin(self, origin):
        """Override to enable support for allowing alternate origins.

        The ``origin`` argument is the value of the ``Origin`` HTTP
        header, the url responsible for initiating this request.  This
        method is not called for clients that do not send this header;
        such requests are always allowed (because all browsers that
        implement WebSockets support this header, and non-browser
        clients do not have the same cross-site security concerns).

        Should return True to accept the request or False to reject it.
        By default, rejects all requests with an origin on a host other
        than this one.

        This is a security protection against cross site scripting attacks on
        browsers, since WebSockets are allowed to bypass the usual same-origin
        policies and don't use CORS headers.

        To accept all cross-origin traffic (which was the default prior to
        Tornado 4.0), simply override this method to always return true::

            def check_origin(self, origin):
                return True

        To allow connections from any subdomain of your site, you might
        do something like::

            def check_origin(self, origin):
                parsed_origin = urllib.parse.urlparse(origin)
                return parsed_origin.netloc.endswith(".mydomain.com")

        .. versionadded:: 4.0
        """
        parsed_origin = urlparse(origin)
        origin = parsed_origin.netloc
        origin = origin.lower()

        host = self.request.headers.get("Host")
        # Check to see that origin matches host directly, including ports
        return origin.startswith('localhost') or origin == host
