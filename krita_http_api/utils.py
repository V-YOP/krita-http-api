import uuid
from dataclasses import dataclass
from datetime import datetime
import time
from functools import wraps
from typing import Callable, Any, Optional

from PyQt5.QtGui import QIcon, QImage

from PyQt5.QtWidgets import QInputDialog, QLineEdit, QToolButton, QAction

from krita import *
from xml.etree.ElementTree import *

from PyQt5.QtCore import qInfo, qWarning, qFatal, QObject, QTextCodec, QByteArray, QBuffer

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
    if window is None:
        return None
    
    view = window.activeView()
    if view is None or view.document() is None:
        return None
    return view

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

def qimage_to_png_base64(image: QImage) -> str:
    """
    convert QImage to png base64 string, MIME-type header included
    """
    # 确保图像格式为RGBA8888
    if image.format() != QImage.Format_RGBA8888:
        image = image.convertToFormat(QImage.Format_RGBA8888)
    
    # 使用QByteArray和QBuffer将QImage写入字节数组
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, 'PNG')
    buffer.close()
    
    return 'data:image/png;base64,' + str(byte_array.toBase64(), 'utf-8')



def __get_menu_structure(menu):
    structure = []
    for action in menu.actions():
        if action.menu():  # If the action has a submenu
            structure.append(__get_menu_structure(action.menu()))
        else:
            structure.append(action)
    return structure

def __get_menubar_structure(menubar):
    structure = []
    for action in menubar.actions():
        if action.menu():  # If the action has a submenu
            structure.append(__get_menu_structure(action.menu()))
    return structure


# window objectName to menu structure
__menu_structure = {}
def get_menus():
    """
    菜单树结构，元素为：
    type Res = Node[]
    type Node = QAction | Node[]
    """
    win = Krita.instance().activeWindow().qwindow()
    name = win.objectName()
    if name in __menu_structure:
        return __menu_structure[name]
    
    __menu_structure[name] = __get_menu_structure(win.menuBar())
    return __menu_structure[name]

def get_active_theme() -> str:
    themes: list[QAction] = get_menus()[8][10]
    return next((x.text() for x in themes if x.isChecked()), None)


def menu_desc(lst, parent_idx = None):
    if parent_idx is None:
        parent_idx = []

    res = []
    for i, menu_item in enumerate(lst):
        if isinstance(menu_item, list):
            res.append(menu_desc(menu_item, [*parent_idx, i]))
        else:
            res.append(menu_item.objectName() + ': ' + '-'.join(map(str,[*parent_idx, i])))
    return res

def uniq(lst):
    return list(dict.fromkeys(lst))