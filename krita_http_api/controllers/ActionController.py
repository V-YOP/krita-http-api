"""
get and trigger actions in krita
"""

from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

ACTION_TIMEOUT = 3 # s

@route('action/list')
def action_list(_):
    res = {}
    for action in Krita.instance().actions():
        res[action.objectName()] = dict(
            shortcuts=QKeySequence.listToString(action.shortcuts()),
            toolTip=action.toolTip(),
            checkable=action.isCheckable(),
            checked=action.isChecked(),
            enabled=action.isEnabled(),
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

latest_actions: list[Tuple[str, datetime]] = []

@route('action/listen')
def action_listen(_):
    """
    获取最近（必须是3秒内）按下的actions的列表
    """
    __init()
    global latest_actions
    if len(latest_actions) == 0:
        return []
    
    now = datetime.now()
    valid_actions = list(map(lambda x: x[0], filter(lambda x: (now - x[1]).seconds < ACTION_TIMEOUT, latest_actions)))
    latest_actions = []
    return valid_actions
    
__fst_run = True
def __init():
    global __fst_run 
    if not __fst_run:
        return
    __fst_run = False

    # 监听所有 action
    actions = Krita.instance().actions()
    for action in actions:
        def go(action: QAction):
            def mygo():
                global latest_actions
                # 移除3秒前的action
                now = datetime.now()
                latest_actions.append((action.objectName(), datetime.now()))
                latest_actions = list(filter(lambda x: (now - x[1]).seconds < ACTION_TIMEOUT, latest_actions))
            return mygo
        action.triggered.connect(go(action))

