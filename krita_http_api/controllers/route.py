from ..HttpRouter import HttpRouter
router = HttpRouter()

def route(code: str):
    def decorator(func):
        router.add_route(code, func)
        return func
    return decorator

