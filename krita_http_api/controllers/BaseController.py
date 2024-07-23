"""
basic API, like health check, API list, display floating message and some test API
"""
from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer, QByteArray, QBuffer, QSize
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication

def current_style():
    Krita.instance().activeWindow()

current_style()

@route('ping')
def ping(req):
    return {
        'msg': 'pong',
        'req': req,
    }

DARK_SELECT_ICON_BASE64 = 'data:image/png;base64,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'
LIGHT_SELECT_ICON_BASE64 = 'data:image/png;base64,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"'

@route('theme')
def theme(_):
    base64 = icon(dict(iconName='select'))
    if base64 == DARK_SELECT_ICON_BASE64: return 'dark' 
    if base64 == LIGHT_SELECT_ICON_BASE64: return 'light'

    raise Exception('unknown theme')

@route('icon')
def icon(req):
    VALID_MODE = ['Normal', 'Disabled', 'Active', 'Selected']
    VALID_STATE = ['On', 'Off']
    assert isinstance(req, dict), 'param must be json object'
    assert (iconName := req.get('iconName')) and isinstance(iconName, str), 'iconName must be string'
    assert (size := req.get('size')) is None or (isinstance(size, list) and len(size) == 2 and all(map(lambda x: isinstance(x, int), size))), 'size must be [int, int]'
    assert (mode := req.get('mode')) is None or mode in VALID_MODE, f"mode must in {VALID_MODE}"
    assert (state := req.get('state')) is None or state in VALID_STATE, f"mode must in {VALID_STATE}"
    
    icon = Krita.instance().icon(iconName)
    if icon.isNull():
        raise ResponseFail(f"icon {req} not found")
    
    size = size if size is not None else [200, 200]
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

    return qimage_to_base64(image)

@route('route-list')
def route_list(_):
    return list(router.routers.keys())

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


def qimage_to_base64(image: QImage) -> str:
    # 确保图像格式为RGBA8888
    if image.format() != QImage.Format_RGBA8888:
        image = image.convertToFormat(QImage.Format_RGBA8888)
    
    # 使用QByteArray和QBuffer将QImage写入字节数组
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, 'PNG')
    buffer.close()
    
    return 'data:image/png;base64,' + str(byte_array.toBase64(), 'utf-8')


