"""
get and trigger actions in krita
"""

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

@route('action/checked', {
    'action': str,
})
def action_checked(req):
    action_name = req.get('action')
    action = Krita.instance().action(action_name)
    assert action is not None, f"action '{action_name}' not found"
    assert action.isCheckable(), f"action '{action_name}' is not checkable"

    return action.isChecked()

@route('action/act', {
    'action': str,
    'act': {'checked', 'unchecked', 'trigger'}
})
def action_act(req):
    action_name = req.get('action')
    act = req.get('act')
    
    action = Krita.instance().action(action_name)
    assert action is not None, f"action '{action_name}' not found"

    if act in ['checked', 'unchecked']:
        assert action.isCheckable(), f"action '{action_name}' is not checkable"
        action.setChecked(True if act == 'checked' else False)
    else:
        action.trigger()

