import os
import uuid
from dataclasses import dataclass
from datetime import datetime
import time
from functools import wraps
from typing import Callable, Any, Dict, List, Optional, Type, TypeVar

from PyQt5.QtGui import QIcon, QImage

from PyQt5.QtWidgets import QInputDialog, QLineEdit, QToolButton, QAction, QWidget

from krita import *
from xml.etree.ElementTree import *

from PyQt5.QtCore import qInfo, qWarning, qFatal, QObject, QTextCodec, QByteArray, QBuffer

from .PerWindowCachedState import PerWindowCachedState

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
        # logger.info(f"cannot display floating message cause no active document")
        return False
    # logger.info(f"display floating message, msg: {message}")
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
        # logger.info(f'call {func.__name__} cost: {end_time - start_time}')

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

def convert_to_kra(img_path: str) -> str:
    """转换图像文件到 kra，返回保存后文件的路径（为图像所在目录）；抛出异常如果文件不存在或非图像文件"""
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"file '{img_path}' doesn't exist.")
    doc = Krita.instance().openDocument(img_path)
    if doc is None:
        # 如果文件非合法图像，Krita会弹窗报错并阻塞，doc会为None，考虑由用户去保证该文件时图像
        raise RuntimeError(f"file '{img_path}' image format illegal.")
    doc.setBatchmode(True)
    dirname = os.path.dirname(img_path)
    file_basename, _ = os.path.splitext(img_path)
    if not doc.saveAs(os.path.join(dirname, f"{file_basename}.kra")):
        raise RuntimeError("WTF?")
    doc.close()


class TimeWatch:
    def __init__(self) -> None:
        self.times: Dict[str, List[float]] = {}

    def watch(self, name: str):
        that = self
        class __MeasureMe:
            def __init__(self) -> None:
                self.start = None

            def __enter__(self):
                self.start = time.perf_counter()

            def __exit__(self, *arg):
                end = time.perf_counter()
                res = round((end - self.start) * 1000, 3)
                if name not in that.times:
                    that.times[name] = [res]
                else:
                    that.times[name].append(res)

        return __MeasureMe()

    def result(self) -> Dict[str, Dict[str, float]]:
        detailed_result = {}
        for name, values in self.times.items():
            if len(values) <= 1:
                continue
            values = values[1:]
            average = sum(values) / len(values)
            maximum = max(values)
            minimum = min(values)

            detailed_result[name] = {
                'average': average,
                'maximum': maximum,
                'minimum': minimum,
                'count': len(values) if isinstance(values, list) else 1
            }
        return detailed_result
    

T = TypeVar('T', bound=QWidget)
def find_widget_by_tooltip(parent: QWidget, type: Type[T], tooltip: str) -> T:
    res = []
    for child in parent.findChildren(type):
        if tooltip == child.toolTip():
            res.append(child)
    if len(res) == 0:
        return 
    return res[0] # TODO raise exception when multiple results?

# works for every tool except Select Shapes Tool
def __get_tool_option_widget_wrapper(window: Window) -> QWidget:
    """
    return a Qwidget, whose last children would be current tool option widget
    """
    for tool_option_docker in window.dockers():
        if tool_option_docker.objectName() == "sharedtooldocker":
            break
    box = tool_option_docker.children()[4].children()[0].children()[0]
    return box 
    # if len(box) == 1:
    #     return 
    
    # print(box[-1].objectName())
    # return box[-1]

tool_option_widget = PerWindowCachedState(__get_tool_option_widget_wrapper)



# pixel_selection = find_widget_by_tooltip(tool_option_docker, QToolButton, Krita.instance().krita_i18nc("@info:tooltip", "Pixel Selection"))
# vector_selection = find_widget_by_tooltip(tool_option_docker, QToolButton, Krita.instance().krita_i18nc("@info:tooltip", 'Vector Selection'))

# print(f"{pixel_selection.isChecked()=}")
# print(f"{vector_selection.isChecked()=}")