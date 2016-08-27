import sys
from tornado import web, ioloop, websocket


class CorsHandler(web.RequestHandler):
    def options(self, *args, **kwargs):
        pass


class EchoWebSocket(websocket.WebSocketHandler):

    def check_origin(self, origin):
        return origin in self.allowed_origins

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        # self.write_message(u"You said: " + message)
        pass

    def on_close(self):
        print("WebSocket closed")


def start_messaging_server(port, allowed_origins):
    app = web.Application([
        ('/websocket', EchoWebSocket, dict(
            allowed_origins=allowed_origins,
        ),),
    ])
    app.listen(port)
    sys.stdout.write("Starting tornado server at port %s\n" % (port, ))
    ioloop.IOLoop.instance().start()
