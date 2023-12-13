from services.runescape_service import RunescapePricesAPI
import tornado.websocket
import tornado.ioloop
import tornado.web
import json

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    """
        ws.send('{"action": "elements"}')
        ws.send('{"action": "data_for_page", "page_number": 1}')
        ws.send('{"action": "disconnect"}')
    """
    def on_message(self, message):
        message = self.parse_message(message)
        data_to_send = self.dipatch_from_message(message)
        self.write_message(json.dumps(data_to_send))

    def on_close(self):
        print("WebSocket closed")

    def parse_message(self, message):
        return json.loads(message)

    def dipatch_from_message(self, message: dict):
        dispatch = {
            'data_for_page': self.get_data_for_page,
            'elements': self.get_all_elements,
            'disconnect': self.disconnect
        }

        action = message.get('action', 'disconnect')
        return dispatch.get(action)(message)

    def get_all_elements(self, _message):
        api = RunescapePricesAPI()
        return api.get_all_items()

    def get_data_for_page(self, message):
        id = message.get('page_number', 1)
        api = RunescapePricesAPI()
        return api.get_paged_items_prices(id)

    def disconnect(self, _message):
        pass

def main():
    app = tornado.web.Application(
        [(r"/websocket/", EchoWebSocket)],
        websocket_ping_timeout=10
    )
    app.listen(8888)

    io_loop = tornado.ioloop.IOLoop.current()

    io_loop.start()


if __name__ == "__main__":
    main()
