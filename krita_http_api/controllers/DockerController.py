"""
get and set docker display status
"""
from ..json_validate import Nullable
from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtWidgets import QDockWidget, QWidget

# windowObjectName+dockerObjectName
docker_original_titlebar_bucket = {}

def docker_headless(docker: QDockWidget):
    print(Krita.instance().activeWindow().dockers()[0].window().objectName())
    res = docker.titleBarWidget().objectName().startswith(f"EMPTY_")

    docker_id = docker.window().objectName() + docker.objectName()
    if docker_id not in docker_original_titlebar_bucket:
        if res:
            pass # 没有缓存时已经没有header了，这说明它的header被其他人丢掉了，这时候什么都做不了
        else:
            docker_original_titlebar_bucket[docker_id] = docker.titleBarWidget()
    return res

def set_docker_headless(docker: QDockWidget, headless: bool):
    if docker_headless(docker) == headless:
        return
    
    if headless:
        x = QWidget()
        x.setObjectName(f"EMPTY_{docker.objectName()}")
        docker.setTitleBarWidget(x)
    else:
        docker_id = docker.window().objectName() + docker.objectName()
        if old_titlebar := docker_original_titlebar_bucket.get(docker_id):
            x = docker.titleBarWidget()
            docker.setTitleBarWidget(old_titlebar)
            x.deleteLater()
        

@route('docker/list')
def docker_list(_):
    res = {}
    for docker in Krita.instance().dockers():
        geo = docker.geometry()
        res[docker.objectName()] = dict(
            visible=docker.isVisible(),
            floating=docker.isFloating(),
            withHeader=not docker_headless(docker)
        )
        if docker.isFloating():
            res[docker.objectName()]['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()],
    return res

@route('docker/get-state', str)
def docker_list(objectName):
    docker = next((i for i in Krita.instance().dockers() if i.objectName() == objectName), None)
    if docker is None:
        raise ResponseFail(f"No docker named '{objectName}'")
    geo = docker.geometry()
    return dict(
        objectName=objectName,
        visible=docker.isVisible(),
        floating=docker.isFloating(),
        pos=[geo.x(), geo.y()],
        size=[geo.width(), geo.height()],
        withHeader=not docker_headless(docker)
    )

@route('docker/set-state', {
    'objectName': str,
    'visible': Nullable(bool),
    'floating': Nullable(bool),
    'pos': Nullable((int, int)),
    'size': Nullable((int, int)),
    'withHeader': Nullable(bool),
})
def docker_setstate(req):
    assert isinstance(req, dict), 'param must be json object'
    objectName = req['objectName']
    visible = req.get('visible')
    floating = req.get('floating')
    pos = req.get('pos')
    size = req.get('size')
    with_header = req.get('withHeader')

    docker = next((i for i in Krita.instance().dockers() if i.objectName() == objectName), None)
    if docker is None:
        raise ResponseFail(f"No docker named '{objectName}'")

    res = {'objectName': objectName}
    if visible is not None:
        geo = docker.geometry()
        docker.setVisible(visible)
        docker.setGeometry(geo)
        res['visible'] = visible
    if floating is not None:
        docker.setFloating(floating)
        res['floating'] = floating

    if pos is not None or size is not None:
        geo = docker.geometry()
        res['oldgeo'] = [geo.x(), geo.y(), geo.width(), geo.height()]
        if pos is not None:
            geo.setX(pos[0])
            geo.setY(pos[1])
            res['pos'] = pos
        if size is not None:
            geo.setWidth(size[0])
            geo.setHeight(size[1])
            res['size'] = size
        docker.setGeometry(geo)
        docker.repaint()
        geo = docker.geometry()
        res['newgeo'] = [geo.x(), geo.y(), geo.width(), geo.height()]

    if with_header is not None:
        set_docker_headless(docker, not with_header)
    return res

@route('docker/hide-all')
def docker_hide(_):
    for docker in Krita.instance().dockers():
        Krita.instance().activeWindow().dockers()[0].window()
        docker.setVisible(False)
