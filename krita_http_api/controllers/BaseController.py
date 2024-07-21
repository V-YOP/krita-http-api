from .route import route, router
from typing import Any
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer

@route('ping')
def ping(req):
    return {
        'msg': 'pong',
        'req': req,
    }

@route('route-list')
def route_list(_):
    return list(router.routers.keys())

@route('current-tool-get')
def current_tool_get(_):
    return current_tool()

@route('current-tool-set')
def current_tool_get(req):
    return set_current_tool(req)

@route('floating-message')
def current_tool_get(req):
    return floating_message(**req)

@route('sync-test')
def sync_test(req):
    return {
        'req': req,
    }

@route('sync-except-test')
def sync_except_test(req):
    return 1 / 0

@route('async-ok-test')
def async_ok_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    def go():
        ok({'req': req, "desc": "this is response body"})
    QTimer.singleShot(100, go)

@route('async-fail-test')
def async_fail_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    def go():
        fail("this is fail message", {'req': req, "desc": "this is response body"})
    QTimer.singleShot(100, go)

@route('async-timeout-test')
def async_timeout_test(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    pass
    # when ok and fail is not invoked (like you forget to call it, or some exception arised) for 5 s, it will timeout and respond a error message

@route('get-image')
def get_image(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    doc = active_document()
    if doc is None:
        return fail("No active document", None)
    # if doc.colorDepth() != 'U8' or doc.colorModel() != 'RGBA':
    #     return fail(f"Only RGBA 8-bit is supported, got {doc.colorModel} {doc.colorDepth}", None)
    w = doc.width()
    h = doc.height()
    depth = doc.colorDepth()
    model = doc.colorModel()
    
    image_bytes = doc.pixelData(0, 0, w, h) # Blue, Green, Red, Alpha
    base64 = str(image_bytes.toBase64(), 'utf-8')
    return ok({
        'w': w, 'h': h, 'depth': depth, 'model': model, 'image': base64
    })
