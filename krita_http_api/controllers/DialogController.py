"""
display dialog for user interaction.
every dialog which need user to respond will have a dialogId, which will identify dialog for client. 
client should query response by dialogId in duration. 
"""

from ..QtEnum import MessageBoxStandardButton, MessageBoxIcon
from ..Form import create_form
from ..HttpRouter import ResponseFail
from .route import route, router
from ..json_validate import Nullable
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# dialogId -> taskResponse
dialog_status: dict[str, dict] = {}
IconType = {*MessageBoxIcon.str_values()}
ButtonType = {*MessageBoxStandardButton.str_values()}
@route('dialog/msg-box', {
    'msg': str,
    'title': Nullable(str),
    'icon': Nullable(IconType),
    'buttons': Nullable([ButtonType]),
    'defaultButton': Nullable(ButtonType),
    'blocking': Nullable(bool), # blocking user interaction with other windows, default is false
})
def msg_box(req: dict):
    """
    type Response = {
        type: 'PENDING',
    } | {
        type: 'EXIT'
    } | {
        type: 'OK',
        button: ButtonType
    }
    """
    box = QMessageBox(Krita.instance().activeWindow().qwindow())
    box.setWindowTitle(req.get('title', ''))
    box.setText(req['msg'])
    box.setMinimumSize(200, 100)
    box.resize(200, 100)
    icon_str = req.get('icon', MessageBoxIcon.to_str(MessageBoxIcon.raw.Information))
    box.setIcon(MessageBoxIcon.from_str(icon_str))

    button_strs = req.get('buttons', [MessageBoxStandardButton.to_str(MessageBoxStandardButton.raw.Ok)])
    
    buttons = None
    for button_str in button_strs:
        button = MessageBoxStandardButton.from_str(button_str)

        if buttons is None:
            buttons = button
        else:
            buttons = buttons | button
    box.setStandardButtons(buttons)

    default_button_str = req.get('defaultButton', MessageBoxStandardButton.to_str(MessageBoxStandardButton.raw.Ok))
    box.setDefaultButton(MessageBoxStandardButton.from_str(default_button_str))

    if req.get('blocking', False):
        box.setModal(True)
    else:
        box.setModal(False)
    
    id = str(uuid.uuid4())
    dialog_status[id] = {'type': 'PENDING'}
    def go(result):
        res_type = MessageBoxStandardButton.to_str(result)
        if res_type is None:
            dialog_status[id] = {'type': 'EXIT'}
        else:
            dialog_status[id] = {'type': 'OK', 'button': res_type}

    box.finished.connect(go)
    box.open()
    return id


# @route('dialog/dialog', {
#     'form': dict,
#     'title': Nullable(str),
#     'buttons': Nullable([ButtonType]),
#     'blocking': Nullable(bool), 
# })
# def dialog(req):
#     form_widget, get_values = create_form(req['form'])

#     dialog = QDialog(Krita.instance().activeWindow().qwindow())
#     dialog.setLayout(QVBoxLayout())
#     dialog.setWindowTitle(req.get('title', ''))
#     if req.get('blocking', False):
#         dialog.setModal(True)
#     else:
#         dialog.setModal(False)

#     button_strs = req.get('buttons', ['APPLY', 'CANCEL'])
#     buttons = None
#     for button_str in button_strs:
#         button = str_to_msgbox_standard_button(button_str)
#         if buttons is None:
#             buttons = button
#         else:
#             buttons = buttons | button

#     button_box = QDialogButtonBox(buttons)
    
#     dialog.layout().addWidget(form_widget)
#     dialog.layout().addWidget(button_box)
    
#     # TODO 我懒了，写不动了


@route('dialog/result', str)
def result(dialog_id, ok, fail):
    if dialog_id not in dialog_status:
        return fail(f'No dialog with id {dialog_id}', None)
    res = dialog_status[dialog_id]
    if res['type'] != 'PENDING':
        del dialog_status[dialog_id]
    return ok(res)