from ..HttpRouter import HttpRouter
router = HttpRouter()

def route(code: str, req_shape = None):
    def decorator(func):
        router.add_route(code, func, req_shape)
        return func
    return decorator

