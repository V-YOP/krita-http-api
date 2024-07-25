"""
basic API, like health check, API list, display floating message and some test API
"""
from ..json_validate import Nullable
from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer, QByteArray, QBuffer, QSize
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication

@route('ping')
def ping(req):
    return {
        'msg': 'pong',
        'req': req,
    }

@route('icon', {
    'iconName': str,
    'size': Nullable((int, int)),
    'mode': Nullable({'Normal', 'Disabled', 'Active', 'Selected'}),
    'state': Nullable({'On', 'Off'})
})
def icon(req):
    iconName = req.get('iconName') 
    size = req.get('size') or [200,200]
    mode = req.get('mode') or 'Normal'
    state = req.get('state') or 'Off'
    
    icon = Krita.instance().icon(iconName)
    if icon.isNull():
        raise ResponseFail(f"icon {req} not found")
    
    if mode == 'Normal':
        mode = QIcon.Mode.Normal
    elif mode == 'Disabled':
        mode = QIcon.Mode.Disabled
    elif mode == 'Active':
        mode = QIcon.Mode.Active
    elif mode == 'Selected':
        mode = QIcon.Mode.Selected
    else:
        mode = QIcon.Mode.Normal
    
    if state == 'On':
        state = QIcon.State.On
    elif state == 'Off':
        state = QIcon.State.Off
    else:
        state = QIcon.State.Off

    # 将QIcon转换为QPixmap
    pixmap = icon.pixmap(QSize(size[0], size[1]), mode=mode, state=state)
    # 将QPixmap转换为QImage
    image = pixmap.toImage()

    return qimage_to_png_base64(image)

@route('route-list')
def route_list(_):
    return list(router.routers.keys())

@route('floating-message', {
    'message': str,
    'timeout': Nullable(int),
    'priority': Nullable(int),
})
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
