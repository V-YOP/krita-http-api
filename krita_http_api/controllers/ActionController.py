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

@route('action/checked')
def action_checked(req):
    assert isinstance(req, dict), 'param must be a json object'
    assert (action_name := req.get('action')) is not None and isinstance(action_name, str), 'action must be a str'

    action = Krita.instance().action(action_name)
    assert action is not None, f"action '{action_name}' not found"
    assert action.isCheckable(), f"action '{action_name}' is not checkable"

    return action.isChecked()

@route('action/act')
def action_act(req):
    VALID_REQ = ['checked', 'unchecked', 'trigger']
    assert isinstance(req, dict), 'param must be a json object'
    assert (action_name := req.get('action')) is not None and isinstance(action_name, str), 'action must be a str'
    assert (act := req.get('act')) is not None and act in VALID_REQ, f'act must in {VALID_REQ}'

    action = Krita.instance().action(action_name)
    assert action is not None, f"action '{action_name}' not found"

    if act in ['checked', 'unchecked']:
        assert action.isCheckable(), f"action '{action_name}' is not checkable"
        action.setChecked(True if act == 'checked' else False)
    else:
        action.trigger()

