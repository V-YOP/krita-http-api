"""
register remote shortcut: when shortcut is invoked, cache it and wait client to `pull` it.
registered shortcuts are transient, which will be removed when krita exit.
"""
from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

registered_shortcuts = {}

latest_shortcut = None
@route("remote-shortcut/current")
def current_shortcut(_):
    pass

@route('remote-shortcut/list')
def shortcut_list(_):
    pass

@route('remote-shortcut/register', {
    'actionId': str,
    'shortcut': str,
})
def shortcut_register(req):
    Krita.instance().windows()
    pass

@route('remote-shortcut/remove')
def a(_):
    pass

