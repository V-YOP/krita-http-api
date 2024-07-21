from typing import Any
from krita import *
from .HttpRouter import HttpRouter
from .QHttpServer import QHTTPServer
from .utils import *
from PyQt5.QtCore import QTimer

logger = Logger()
router = HttpRouter()

def sync_test(req: Any):
    return {
        'req': req,
    }

def sync_except_test(req: Any):
    return 1 / 0

def async_ok_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    def go():
        ok({'req': req, "desc": "this is response body"})
    QTimer.singleShot(100, go)

def async_fail_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    def go():
        fail("this is fail message", {'req': req, "desc": "this is response body"})
    QTimer.singleShot(100, go)

def async_timeout_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    pass
    # when ok and fail is not invoked (like you forget to call it, or some exception arised) for 5 s, it will timeout and respond a error message



ROUTERS = {
    'route-list': lambda _: list(router.routers.keys()),
    'current-tool-get': lambda _: current_tool(),
    'current-tool-set': lambda req: set_current_tool(req),
    'floating-message': lambda req: floating_message(**req),

    'sync-test': sync_test,
    'sync-except-test': sync_except_test,
    'async-ok-test': async_ok_test,
    'async-fail-test': async_fail_test,
    'async-timeout-test': async_timeout_test,
}


for key, value in ROUTERS.items():
    router.add_route(key, value)

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
