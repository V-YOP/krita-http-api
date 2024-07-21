import uuid
from dataclasses import dataclass
from datetime import datetime
import time
from functools import wraps
from typing import Callable, Any, Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QToolButton

from krita import *
from xml.etree.ElementTree import *

from PyQt5.QtCore import qInfo, qWarning, qFatal, QObject

from PyQt5.QtCore import QTextCodec

from .Logger import Logger

logger = Logger()


def user_input(label: str,
               done_callback: Callable[[str], Any],
               reject_callback: Callable[[str], Any] = lambda x: None) -> None:
    """
    open a dialog waiting for user input, then call callback when dialog closed
    :param label: input label
    :param done_callback: call when accepted
    :param reject_callback: call when rejected
    """
    # TODO use QInputDialog.getText
    dialog = QInputDialog()
    dialog.setLabelText(label)
    dialog.accepted.connect(lambda: done_callback(dialog.textValue()))
    dialog.rejected.connect(lambda: reject_callback(dialog.textValue()))
    dialog.exec()  # exec will block the parent event loop! if async execute is needed, use open() instead


def floating_message(message: str, icon=QIcon(), timeout=3000, priority=2) -> bool:
    """
    display floating message with a optional icon
    :param message: msg
    :param icon:
    :param timeout: ms
    :param priority: 0 = High, 1 = Medium, 2 = Low
    :return: return true if display message successfully
    """
    if active_document() is None:
        logger.info(f"cannot display floating message cause no active document")
        return False
    logger.info(f"display floating message, msg: {message}")
    active_view().showFloatingMessage(message, icon, timeout, priority)
    return True


def active_window() -> Window | None:
    return Krita.instance().activeWindow()


def active_view() -> View | None:
    window = active_window()
    return None if window is None else window.activeView()


def active_document() -> Document | None:
    view = active_view()
    return None if view is None else view.document()


def active_layer() -> Node | None:
    document = active_document()
    return None if document is None else document.activeNode()


def find_tool_box() -> QToolButton:
    qwindow = active_window().qwindow()
    for qobj in qwindow.findChildren(QObject):
        if qobj.metaObject().className() == "KoToolBox":
            return qobj


childrenCache: list[QToolButton] = None
def current_tool() -> Optional[str]:
    global childrenCache

    if not childrenCache:
        toolbox = find_tool_box()
        if toolbox is None:
            return None
        childrenCache = toolbox.findChildren(QToolButton)

    for child in childrenCache:
        try:
            if child.isChecked():
                return child.objectName()
        except BaseException as e:
            continue
    return None

def set_current_tool(toolName: str):
    global childrenCache
    if not childrenCache:
        toolbox = find_tool_box()
        if toolbox is None:
            return None
        childrenCache = toolbox.findChildren(QToolButton)
    for child in childrenCache:
        if child.objectName() == toolName:
            child.click()
            return
    raise NameError(f"Unknown tool: {toolName}")

def action_shortcuts() -> dict[str, str]:
    res = {}
    for action in Krita.instance().actions():
        if not action.shortcut().isEmpty():
            res[action.objectName()] = action.shortcut().toString()
    return res


def timemeter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        func(*args, **kwargs)
        end_time = datetime.now()
        logger.info(f'call {func.__name__} cost: {end_time - start_time}')

    return wrapper


"""
<document-info xmlns= "http://www.calligra.org/DTD/document-info "> 
<about> 
    <title>MyDocument</title> 
    <description></description> 
    <subject></subject> 
    <abstract><![CDATA[]]></abstract> 
    <keyword></keyword> 
    <initial-creator>Unknown</initial-creator> 
    <editing-cycles>1</editing-cycles> 
    <editing-time>35</editing-time> 
    <date>2017-02-27T20:15:09</date> 
    <creation-date>2017-02-27T20:14:33</creation-date>
     <language></language> 
 </about> 
 <author> 
 <full-name >BoudewijnRempt</full-name > 
 <initial></initial> 
 <author-title></author-title>
  <email></email> 
  <telephone></telephone> 
  <telephone-work></telephone-work>
   <fax></fax>
    <country></country> 
    <postal-code></postal-code> 
    <city></city> 
    <street></street> 
    <position></position> 
    <company></company> 
    </author> 
</document-info>
"""

@dataclass
class DocumentInfo:
    id: str
    title: str
    edit_time: int
    create_date: datetime
    update_date: datetime
    document: Document


    @staticmethod
    def from_document(document: Document) -> Optional["DocumentInfo"]:
        xml: Element = fromstring(document.documentInfo())

        def elem_text(tagName: str):
            res = xml.findall('.//{*}' + tagName)[0].text
            return "" if res is None else res

        desc_elem = xml.findall(".//{*}description")[0]
        if desc_elem.text is None or not desc_elem.text.startswith("ID="):
            uniqueId = str(uuid.uuid4())
            desc_elem.text = f"ID={uniqueId}\n{'' if desc_elem.text is None else desc_elem.text}"
            document.setDocumentInfo(tostring(xml, 'unicode', default_namespace="http://www.calligra.org/DTD/document-info"))
        else:
            uniqueId = desc_elem.text[3:3+len(str(uuid.uuid4()))]

        title = elem_text("title")
        edit_time = 0
        if elem_text("editing-time") != '':
            edit_time = int(elem_text("editing-time"))

        date_format = "%Y-%m-%dT%H:%M:%S"
        create_date = datetime.strptime(elem_text("creation-date"), date_format)
        update_date = datetime.strptime(elem_text("date"), date_format)
        if uniqueId is None:
            raise Exception()
        return DocumentInfo(uniqueId, title, edit_time, create_date, update_date, document)

def singleton(cls):
    """
    a singleton decorator
    """
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
