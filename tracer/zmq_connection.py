from __future__ import unicode_literals
import zmq
import threading


class ZMQClientThread(threading.Thread):

    def __init__(self, callback, host="*", port="8882"):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (host, port,))
        self.callback = callback

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            #  Wait for next request from client
            message = self.socket.recv()
            self.callback(message)
            self.socket.send_string("OK")
