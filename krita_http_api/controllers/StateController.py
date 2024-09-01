"""
get and set global state in krita, like brush preset, painting opacity, brush size, blending Mode... 
some checked action which is useful for painting is also included, like 'canvas only' and 'eraser mode'...
"""

from ..json_validate import Nullable
from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple, List
from krita import *
from ..utils import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import time


@route('state/get')
def state_get(_):
    watch = TimeWatch()
    with watch.watch('getView'):
        view = active_view()
        if view is None:
            raise ResponseFail("No active view")
        
    with watch.watch('tool'):
        res = { 'tool': current_tool() }

    with watch.watch('viewState'):
        res['brushSize'] = view.brushSize()
        res['brushRotation'] = view.brushRotation()
        res['blendingMode'] = view.currentBlendingMode()
        res['brushPreset'] = view.currentBrushPreset().name()
        res['gradient'] = view.currentGradient().name()
        res['pattern'] = view.currentPattern().name()
        res['opacity'] = view.paintingOpacity()
        res['flow'] = view.paintingFlow()
        res['foreground'] = view.foregroundColor().componentsOrdered()
        res['background'] = view.backgroundColor().componentsOrdered()

    with watch.watch('actionState'):
        res['eraserMode'] = Krita.instance().action("erase_action").isChecked()
        res['canvasOnly'] = Krita.instance().action("view_show_canvas_only").isChecked()

    with watch.watch('globalState'):
        res['zoomFactor'] = QApplication.primaryScreen().devicePixelRatio()
        res['theme'] = get_active_theme()

    with watch.watch('documentState'):
        doc = view.document()
        fname = doc.fileName()
        doc_info = DocumentInfo.from_document(doc)
        res['editTime'] = doc_info.edit_time
        res['fileName'] = fname if fname != '' else None
        # when you can deselect, you have selections
        res['withSelection'] = Krita.instance().action('deselect').isEnabled()
        w = doc.width()
        h = doc.height()
        res['picResolution'] = [w, h]

    with watch.watch('toolOption-' + res['tool']):
        res['toolOptions'] = get_tool_option_state(res['tool'])

    with watch.watch('layersState'):
        res['activeLayer'] = None
        if node := doc.activeNode():
            res['activeLayer'] = {
                'activeLayerName': node.name(),
                'activeLayerMode': node.blendingMode(),
                'activeLayerOpacity': node.opacity(),
            }

    res['cost'] = watch.result()
    return res

@route('state/set', {
    'brushSize': Nullable(float),
    'brushRotation': Nullable(float),
    'blendingMode': Nullable(str), # TODO use literal
    'brushPreset': Nullable(str),
    'gradient': Nullable(str),
    'pattern': Nullable(str),
    'opacity': Nullable(str),
    'flow': Nullable(str),
    'tool': Nullable(str),
    'eraserMode': Nullable(bool),
    'canvasOnly': Nullable(bool),
    'foreground': Nullable((float, float, float, float)),
    'background': Nullable((float, float, float, float)),
})
def state_set(req):
    view = active_view()
    if view is None:
        raise ResponseFail("No active view")
    
    res = {}
    if (brushSize := req.get('brushSize')) is not None:
        view.setBrushSize(float(brushSize))
        res['brushSize'] = float(brushSize)
    
    if (brushRotation := req.get('brushRotation')) is not None:
        view.setBrushRotation(float(brushRotation))
        res['brushRotation'] = float(brushRotation)
    
    if (blendingMode := req.get('blendingMode')) is not None:
        view.setCurrentBlendingMode(blendingMode)
        res['blendingMode'] = blendingMode

    if (brushPreset := req.get('brushPreset')) is not None:
        brushPresetResource = Krita.instance().resources('preset').get(brushPreset)
        assert brushPresetResource is not None, f"brushPreset '{brushPreset}' not exists."

        view.setCurrentBrushPreset(brushPresetResource)
        res['brushPreset'] = brushPreset
    
    if (gradient := req.get("gradient")) is not None:
        patternResource = Krita.instance().resources('gradient').get(gradient)
        assert patternResource is not None, f"gradient '{gradient}' not exists."

        view.setCurrentGradient(patternResource)
        res['gradient'] = patternResource

    if (pattern := req.get("pattern")) is not None:
        patternResource = Krita.instance().resources('pattern').get(pattern)
        assert patternResource is not None, f"gradient '{gradient}' not exists."

        view.setCurrentPattern(patternResource)
        res['pattern'] = patternResource

    if (opacity := req.get('opacity')) is not None:
        view.setPaintingOpacity(float(opacity))
        res['opacity'] = float(opacity)

    if (flow := req.get('flow')) is not None:
        view.setPaintingOpacity(float(flow))
        res['flow'] = float(flow)

    if (foreground := req.get('foreground')) is not None:
        view.setForeGroundColor(to_qcolor(foreground))
        res['foreground'] = foreground

    if (background := req.get('background')) is not None:
        view.setBackGroundColor(to_qcolor(background))
        res['background'] = background

    if (tool := req.get('tool')) is not None:
        set_current_tool(tool)
        res['tool'] = tool

    if (eraserMode := req.get('eraserMode')) is not None:
        Krita.instance().action("erase_action").setChecked(eraserMode)
        res['eraserMode'] = eraserMode
        
    if (canvasOnly := req.get('canvasOnly')) is not None:
        Krita.instance().action("view_show_canvas_only").setChecked(canvasOnly)
        res['canvasOnly'] = canvasOnly

    return res


# DARK_SELECT_ICON_10x10_BASE64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAACXBIWXMAABYlAAAWJQFJUiTwAAAAr0lEQVQYlYXMMQrCUBCE4X83WqTwCl4gkRSSVhAES9HaU3gSaysrwcpGEGsvkLz3TmFjZxOStbGIiGaqgfkYAEIIQ+/9mj9RgKqq1Mz23vvlX/hOZGbHoijmXRCgr6on59ykCwLEwDmEkHdBgEHTNFfn3OgXfAKY2VZEVu2h1+qPKIoWdV1fRGSapulGROzjUVWfZjZLkuQGHICsLMv86zHLsjtwBxCRnZmNVTVuwxffIz3Drn/9pAAAAABJRU5ErkJggg=='
# LIGHT_SELECT_ICON_10x10_BASE64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAACXBIWXMAABYlAAAWJQFJUiTwAAAAqElEQVQYlYXOMQrCQBCF4X/GbJHCK3gDsVhmwzaCIFiK1p7Ck1hbWQlWNoJYCyHkKGns0q5NigiSvOrBfMwMAN77WVEUBwaiAM45BS4hhN0g7DIRkVsIYTMGAZyI3M1sOQYBclV9mJmNQYCpqr5ijPO/MKXUdvUkIvv+LOv1D7AFnsCqqqojkH42qmorIuu6rt/AFVjEGH9+zADKsmyApjt/FhEP5H34Ba2XIsZQg9CnAAAAAElFTkSuQmCC'
# dark_select_cachekey = None
# light_select_cachekey = None

# def get_theme():
#     global dark_select_cachekey, light_select_cachekey
#     select_icon = Krita.instance().icon('select')

#     if select_icon.cacheKey() == dark_select_cachekey:
#         return 'dark'
#     if select_icon.cacheKey() == light_select_cachekey:
#         return 'light'

#     base64 = qimage_to_png_base64(select_icon.pixmap(10, 10).toImage())
#     if base64 == DARK_SELECT_ICON_10x10_BASE64: 
#         dark_select_cachekey = select_icon.cacheKey()
#         return 'dark' 
#     if base64 == LIGHT_SELECT_ICON_10x10_BASE64: 
#         light_select_cachekey = select_icon.cacheKey()
#         return 'light'

#     raise Exception('unknown theme')

def to_qcolor(rgba: Tuple[int,int,int,int]) -> ManagedColor:
    res = ManagedColor('RGBA', 'U8', '')
    lst = res.componentsOrdered()
    lst[0] = rgba[0]
    lst[1] = rgba[1]
    lst[2] = rgba[2]
    lst[3] = rgba[3]
    res.setComponents(lst)
    return res
    
# 选取工具的动作选项
SELECT_ACTIONS_TOOLTIP_REVERSE = {
    Krita.instance().krita_i18nc('@info:tooltip', action): action
    for action in ['Replace', 'Intersect', 'Add', 'Subtract', 'Symmetric Difference']
}
# 选取工具的模式选项
SELECT_MODE_TOOLTIP_REVERSE = {
    Krita.instance().krita_i18nc('@info:tooltip', action): action
    for action in ['Pixel Selection', 'Vector Selection']
}
select_tool_option_select_btns = tool_option_widget.chain(lambda parent: [i for i in parent.findChildren(QToolButton) if i.toolTip() in SELECT_ACTIONS_TOOLTIP_REVERSE])
select_tool_option_mode_btns = tool_option_widget.chain(lambda parent: [i for i in parent.findChildren(QToolButton) if i.toolTip() in SELECT_MODE_TOOLTIP_REVERSE])

def get_tool_option_state(tool: str) -> dict:
    res = {}
    match tool:
        case "KritaShape/KisToolBrush":
            pass
        case x if x in ('KisToolSelectOutline',
                'KisToolSelectElliptical',
                'KisToolSelectRectangular',
                'KisToolSelectPolygonal',
                'KisToolSelectSimilar',
                'KisToolSelectMagnetic'):
            res['type'] = 'SELECT_TOOL'

            # actions
            for btn in select_tool_option_select_btns.get(Krita.instance().activeWindow()):
                if btn.isChecked():
                    res['selectAction'] = SELECT_ACTIONS_TOOLTIP_REVERSE[btn.toolTip()]
                    break
            # modes
            for btn in select_tool_option_mode_btns.get(Krita.instance().activeWindow()):
                if btn.isChecked():
                    res['selectMode'] = SELECT_MODE_TOOLTIP_REVERSE[btn.toolTip()]
                    break

    return res
