from typing import Any
from krita import *
from .HttpRouter import HttpRouter
from .QHttpServer import QHTTPServer
from .utils import *
from PyQt5.QtCore import QTimer

from .controllers.route import router

logger = Logger()

class krita_http_api(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.http_server = QHTTPServer(1976)
        # self.http_server.setParent(self)
        self.http_server.on_request(router)
        self.http_server_started = False

    def setup(self):
        pass

    def createActions(self, window):
        if not self.http_server_started:
            self.http_server.start()
            self.http_server_started = True

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(krita_http_api(Krita.instance())) 
