import logging
import websocket

from rackclient.lib import RACK_CTX

LOG = logging.getLogger(__name__)

WS_PORT = 8888


class SignalManager(object):
    def __init__(self, url=None):
        if url:
            self.url = url.rstrip('/')
        else:
            self.url = "ws://" + ':'.join([RACK_CTX.proxy_ip, str(WS_PORT)])

    def receive(self, on_msg_func, pid=None):
        self.on_msg_func = on_msg_func
        if pid:
            header = 'PID: ' + pid
        elif getattr(RACK_CTX, 'pid', False):
            header = 'PID: ' + RACK_CTX.pid
        else:
            raise Exception("Target PID is required.")
        wsapp = websocket.WebSocketApp(
                               url=self.url + '/receive',
                               header=[header],
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        LOG.debug("Started to wait for messages.")
        wsapp.run_forever()

    def on_message(self, ws, message):
        LOG.debug("Received a message: %s" % message)
        if self.on_msg_func(message):
            ws.close()

    def on_error(self, ws, error):
        LOG.error(error)
        ws.close()
        raise Exception("Error ocurred while waiting for messages.")
    
    def on_close(self, ws):
        LOG.debug("Websocket connection %s closed" % ws.header[0])

    def send(self, target_id, message):
        ws = websocket.create_connection(self.url + '/send', header=['PID: ' + target_id])
        LOG.debug("Send a message: %s" % message)
        ws.send(message)
        ws.close()
