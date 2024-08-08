"""
display dialog for user interaction.
every dialog which need user to respond will have a taskId, which will identify dialog for client. 
client should query response by taskId in duration. 
"""

from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

"""
type taskResponse = {
    type: 'PENDING',
} | {
    type: 'EXIT'
} | {
    type: 'OK',
    result: any
}
"""

# taskId -> taskResponse
task_status: dict[str, dict] = {}

@route('dialog/msg-box')
def msg_box(_):
    pass