"""
get and set global state in krita, like brush preset, painting opacity, brush size, blending Mode... 
some checked action which is useful for painting is also included, like 'canvas only' and 'eraser mode'...
"""

from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer

@route('state/get')
def state_get(_):
    view = active_view()
    if view is None:
        raise ResponseFail("No active view")
    res = { 'tool': current_tool() }
    res['brushSize'] = view.brushSize()
    res['brushRotation'] = view.brushRotation()
    res['blendingMode'] = view.currentBlendingMode()
    res['brushPreset'] = view.currentBrushPreset().name()
    res['gradient'] = view.currentGradient().name()
    res['pattern'] = view.currentPattern().name()
    res['opacity'] = view.paintingOpacity()
    res['flow'] = view.paintingFlow()
    res['foreground'] = view.foregroundColor().components()
    res['background'] = view.backgroundColor().components()
    res['eraserMode'] = Krita.instance().action("erase_action").isChecked()
    res['canvasOnly'] = Krita.instance().action("view_show_canvas_only").isChecked()
    doc = view.document()
    fname = doc.fileName()
    res['fileName'] = fname if fname != '' else None

    return res

@route('state/set')
def state_set(req):
    view = active_view()
    if view is None:
        raise ResponseFail("No active view")
    
    res = {}

    if (brushSize := req.get('brushSize')) is not None:
        assert isinstance(brushSize, (int, float)), 'brushSize must be int or float'
        view.setBrushSize(float(brushSize))
        res['brushSize'] = float(brushSize)
    
    if (brushRotation := req.get('brushRotation')) is not None:
        assert isinstance(brushRotation, (int, float)), 'brushRotation must be int or float'
        view.setBrushRotation(float(brushRotation))
        res['brushRotation'] = float(brushRotation)
    
    if (blendingMode := req.get('blendingMode')) is not None:
        assert isinstance(blendingMode, str), 'blendingMode must be str'
        view.setCurrentBlendingMode(blendingMode)
        res['blendingMode'] = blendingMode

    if (brushPreset := req.get('brushPreset')) is not None:
        assert isinstance(brushPreset, str), 'brushPreset must be str'
        brushPresetResource = Krita.instance().resources('preset').get(brushPreset)
        assert brushPresetResource is not None, f"brushPreset '{brushPreset}' not exists."

        view.setCurrentBrushPreset(brushPresetResource)
        res['brushPreset'] = brushPreset
    
    if (gradient := req.get("gradient")) is not None:
        assert isinstance(gradient, str), 'gradient must be str'
        patternResource = Krita.instance().resources('gradient').get(gradient)
        assert patternResource is not None, f"gradient '{gradient}' not exists."

        view.setCurrentGradient(patternResource)
        res['gradient'] = patternResource

    if (pattern := req.get("pattern")) is not None:
        assert isinstance(pattern, str), 'pattern must be str'
        patternResource = Krita.instance().resources('pattern').get(pattern)
        assert patternResource is not None, f"gradient '{gradient}' not exists."

        view.setCurrentPattern(patternResource)
        res['pattern'] = patternResource

    if (opacity := req.get('opacity')) is not None:
        assert isinstance(opacity, (int, float)), 'opacity must be int or float'
        view.setPaintingOpacity(float(opacity))
        res['opacity'] = float(opacity)

    if (flow := req.get('flow')) is not None:
        assert isinstance(flow, (int, float)), 'flow must be int or float'
        view.setPaintingOpacity(float(flow))
        res['flow'] = float(flow)

    if (foreground := req.get('foreground')) is not None:
        assert isinstance(foreground, list) and len(foreground) == 4 and all(map(lambda x: isinstance(x, (int, float)), foreground)), 'foreground must be [float, float, float, float]'
        view.setForeGroundColor(to_qcolor(foreground))
        res['foreground'] = foreground

    if (background := req.get('background')) is not None:
        assert isinstance(background, list) and len(background) == 4 and all(map(lambda x: isinstance(x, (int, float)), background)), 'background must be [float, float, float, float]'
        view.setBackGroundColor(to_qcolor(background))
        res['background'] = background

    if (tool := req.get('tool')) is not None:
        assert isinstance(tool, str), 'tool must be str'
        set_current_tool(tool)
        res['tool'] = tool

    if (eraserMode := req.get('eraserMode')) is not None:
        assert isinstance(eraserMode, bool), 'eraserMode must be bool'
        Krita.instance().action("erase_action").setChecked(eraserMode)
        res['eraserMode'] = eraserMode
        
    if (canvasOnly := req.get('canvasOnly')) is not None:
        assert isinstance(canvasOnly, bool), 'canvasOnly must be bool'
        Krita.instance().action("view_show_canvas_only").setChecked(canvasOnly)
        res['canvasOnly'] = canvasOnly

    return res



def to_qcolor(rgba: Tuple[int,int,int,int]) -> ManagedColor:
    res = ManagedColor('RGBA', 'U8', '')
    lst = res.components()
    lst[0] = rgba[0]
    lst[1] = rgba[1]
    lst[2] = rgba[2]
    lst[3] = rgba[3]
    res.setComponents(lst)
    return res
    