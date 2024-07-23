"""
read and write document and image data
"""

from ..HttpRouter import ResponseFail
from .route import route, router
from typing import Any, Tuple
from krita import *
from ..utils import *
from PyQt5.QtCore import QTimer

@route('get-image')
def get_image(req: Any, ok: Callable[[Any], None], fail: Callable[[str, Any], None]):
    doc = active_document()
    if doc is None:
        return fail("No active document", None)
    # if doc.colorDepth() != 'U8' or doc.colorModel() != 'RGBA':
    #     return fail(f"Only RGBA 8-bit is supported, got {doc.colorModel} {doc.colorDepth}", None)
    w = doc.width()
    h = doc.height()
    depth = doc.colorDepth()
    model = doc.colorModel()
    
    image_bytes = doc.pixelData(0, 0, w, h) # Blue, Green, Red, Alpha
    base64 = str(image_bytes.toBase64(), 'utf-8')
    return ok({
        'w': w, 'h': h, 'depth': depth, 'model': model, 'image': base64
    })

