"""
manage views in current windows.
"""

from ..PerWindowCachedState import PerWindowCachedState
from ..HttpRouter import ResponseFail
from ..json_validate import Nullable
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import math

@route('view/list')
def view_list(_):
    win = Krita.instance().activeWindow()
    views = all_views(win)

    res = []
    for view_id, qview, view in views:
        display_status = 'MAXIMIZED' if qview.isMaximized() else 'MINIMIZED' if qview.isMinimized() else 'NORMAL'
        doc = view.document()
        
        filename = doc.fileName()
        view_frame_geo = qview.geometry()
        area_geo = qview.mdiArea().geometry()
        view_client_geo = qview.contentsRect()

        # view to canvas, view to image, got canvas to image
        canvas_to_image = calculate_transform_from_B_to_C(view.flakeToCanvasTransform(), view.flakeToImageTransform())
        scale = canvas_to_image.m11()
        angle_rad = math.atan2(canvas_to_image.m21(), canvas_to_image.m11())
        # 图像逆时针旋转的角度
        rotation = math.degrees(angle_rad)
        pan = canvas_to_image.dx(), canvas_to_image.dy()
        
        # rotation, = canvas.rotation(), canvas.zoomLevel(), canvas.
        res.append(dict(
            viewId=view_id,
            display=display_status,
            docId=doc.rootNode().uniqueId().toString() + '-' + filename,
            isFile=bool(filename is not None and filename != ''),
            filename=filename,
            frameless=bool(qview.windowFlags() & Qt.FramelessWindowHint),
            stayOnTop=bool(qview.windowFlags() & Qt.WindowStaysOnTopHint),
            viewFrameSize=(view_frame_geo.width(), view_frame_geo.height()),
            viewFramePos=(view_frame_geo.x(), view_frame_geo.y()),
            viewClientSize=(view_client_geo.width(), view_client_geo.height()),
            viewClientPos=(view_client_geo.x(), view_client_geo.y()),
            canvasRotation=rotation,
            canvasScale=scale,
            canvasPan=pan,
            canvasToImageMetrix=(canvas_to_image.m11(), canvas_to_image.m21(), canvas_to_image.m31(), canvas_to_image.m12(), canvas_to_image.m22(), canvas_to_image.m32(), canvas_to_image.m13(), canvas_to_image.m23(), canvas_to_image.m33()),
            areaSize=(area_geo.width(), area_geo.height()),
            areaPos=(area_geo.x(), area_geo.y()),
        ))
    return res

@route('view/set', {
    'viewId': int,
    'display': Nullable({'MAXIMIZED', 'MINIMIZED', 'NORMAL'}),
    'frameless': Nullable(bool),
    'stayOnTop': Nullable(bool),
    'size': Nullable((int, int)),
    'pos': Nullable((int, int)),
})
def set_view(req: dict):
    win = Krita.instance().activeWindow()
    views = all_views(win)
    for view_id, qview, view in views:
        if req['viewId'] == view_id:
            break

    res = {}
    if display := req.get('display'):
        res['display'] = display
        if display == 'MAXIMIZED':
            qview.showMaximized()
        elif display == 'MINIMIZED':
            qview.showMinimized()
        else:
            qview.showNormal()
    
    if (frameless := req.get('frameless')) is not None:
        res['frameless'] = frameless
        qview.setWindowFlag(Qt.FramelessWindowHint, frameless)

    if (stayOnTop := res.get('stayOnTop')) is not None:
        res['stayOnTop'] = stayOnTop
        qview.setWindowFlag(Qt.WindowStaysOnTopHint, stayOnTop)
    return res

log = Logger()
class __ViewsGetter:
    def __init__(self) -> None:
        self.notifier = Krita.instance().notifier()
        def refresh():
            log.info('refresh!!11')
            if not hasattr(self, 'cache'):
                return
            log.info('refresh!!')
            self.cache.clear()
        self.notifier.windowCreated.connect(refresh)
        self.notifier.viewClosed.connect(refresh)
        self.notifier.viewCreated.connect(refresh)
        self.notifier.imageCreated.connect(refresh)

    def __call__(self, window: Window) -> Any:
        self.notifier.setActive(True)
        
        views = window.views()
        if views is None:
            return []
        qviews: list[QMdiSubWindow] = window.qwindow().findChild(QMdiArea).findChildren(QMdiSubWindow)
        def get_view_id(subwin: QMdiSubWindow) -> int:
            view_widget = next((i for i in subwin.findChildren(QWidget) if i.metaObject().className() == 'KisView'), None)
            view_name = view_widget.objectName()
            return int(view_name.replace('view_', ''))
        qviews.sort(key=get_view_id)

        res = []
        for qview, view in zip(qviews, views):
            view_id = get_view_id(qview)
            res.append((view_id, qview, view))
        return res
__view_getter_impl = __ViewsGetter()
__view_getter = PerWindowCachedState(__view_getter_impl)

__view_getter_impl.cache = __view_getter

def all_views(window: Window) -> list[Tuple[int, QMdiSubWindow, View]]:
    return __view_getter.get(window)



# __qarea = PerWindowCachedState(lambda window: window.qwindow().findChild(QMdiArea))
# def all_views(window: Window) -> list[Tuple[int, QMdiSubWindow, View]]:
#     qwindow = window.qwindow()
#     views = window.views()
#     if views is None:
#         return []
#     qviews: list[QMdiSubWindow] = __qarea.get(window).findChildren(QMdiSubWindow)
#     def get_view_id(subwin: QMdiSubWindow) -> int:
#         view_widget = next((i for i in subwin.findChildren(QWidget) if i.metaObject().className() == 'KisView'), None)
#         view_name = view_widget.objectName()
#         return int(view_name.replace('view_', ''))

#     qviews.sort(key=get_view_id)

#     res = []
#     for qview, view in zip(qviews, views):
#         view_id = get_view_id(qview)
#         res.append((view_id, qview, view))
#     return res




def calculate_transform_from_B_to_C(T_AB: QTransform, T_AC: QTransform) -> QTransform:
    """(A->B) -> (A->C) -> (B->C)"""
    # 计算 T_AB 的逆矩阵
    T_AB_inv = T_AB.inverted()[0]
    
    # 计算从 B 到 C 的变换矩阵
    T_BC = T_AB_inv * T_AC
    
    return T_BC
