import tornado.websocket
import tornado.ioloop
import tornado.web

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")

def main():
    app = tornado.web.Application(
      [(r"/websocket", EchoWebSocket)],
      websocket_ping_timeout=10
    )
    app.listen(8888)

    io_loop = tornado.ioloop.IOLoop.current()

    io_loop.start()

if __name__ == "__main__":
    main()