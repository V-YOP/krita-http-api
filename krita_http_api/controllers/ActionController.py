from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

@route('action/list')
def action_list(_):
    res = {}
    for action in Krita.instance().actions():
        res[action.objectName()] = dict(
            shortcuts=QKeySequence.listToString(action.shortcuts()),
            toolTip=action.toolTip(),
            checkable=action.isCheckable(),
            checked=action.isChecked(),
        )
    return res

