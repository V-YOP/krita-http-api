from ..HttpRouter import ResponseFail
from .route import route
from ..utils import *

@route('current-blending-mode-get')
def currentBlendingMode(_):
    view = get_view()
    return view.currentBlendingMode()

@route('current-brush-preset-get')
def currentBrushPreset(_):
    view = get_view()
    return view.currentBrushPreset()

@route('current-gradient-get')
def currentGradient(_):
    view = get_view()
    return view.currentGradient()

@route('current-pattern-get')
def currentPattern(_):
    view = get_view()
    return view.currentPattern()



def get_view():
    view = active_view()
    if view is None:
        raise ResponseFail("No Active View")
    return view