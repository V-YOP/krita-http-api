from krita import *
from .QHttpServer import QHTTPServer
from .utils import *
from PyQt5.QtCore import QTimer
logger = Logger()
class krita_http_api(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.http_server = QHTTPServer(1976)
        # self.http_server.setParent(self)
        self.http_server.on_request(self.go)
        self.http_server_started = False

    def go(self, req: dict, ok, fail):
        delay = req.get('delay')
        delay = delay if isinstance(delay, int) else 0
        def mygo():
            logger.info("Hello, World!")
            try:
                raise BaseException('!!')
            except:
                fail('just test', {
                    'nihao': '世界',
                    'current_tool': current_tool(),
                    'delay': delay,
                })

        QTimer.singleShot(delay, mygo)

    def setup(self):
        pass

    def methodToRunOnClick(self):
        floating_message('HELLO, WORLD!')
        
    def createActions(self, window):
        if not self.http_server_started:
            self.http_server.start()
            self.http_server_started = True

        action = window.createAction("uniqueIdOfAction", "Text shown in menu of the action", "tools/scripts")
        action.triggered.connect(self.methodToRunOnClick)

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(krita_http_api(Krita.instance())) 
