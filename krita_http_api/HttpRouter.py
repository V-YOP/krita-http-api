
from .Logger import Logger
from typing import Any, Callable, Union
import inspect

class ResponseFail(Exception):
    def __init__(self, msg: str, res = None, *args: object) -> None:
        super().__init__(msg, res, *args)
        self.msg = msg
        self.res = res

logger = Logger()

def get_function_params(func):
    if isinstance(func, type):
        # Handle class with __call__ method
        if hasattr(func, '__call__'):
            func = func.__call__
    elif not callable(func):
        raise ValueError(f"{func} is not callable")

    signature = inspect.signature(func)
    return [param.name for param in signature.parameters.values()]

class HttpRouter:
    def __init__(self) -> None:
        self.routers = {}

    def __call__(self, req, ok, fail) -> Any:
        if 'code' not in req:
            return fail(f"field 'code' missing", None)
        if type(req['code']) is not str:
            return fail(f"field 'code' must be string", None)
        if 'param' not in req:
            return fail(f"field 'param' missing", None)
        if req['code'] not in self.routers:
            return fail(f"route '{req['code']}' is not defined. valid routes: {list(self.routers.keys())}", None)
        logger.info(f"request '{req['code']}', param: {req['param']}")
        self.routers[req['code']](req['param'], ok, fail)

    def add_route(self, code: str, cb: Union[Callable[[Any], Any], Callable[[Any, Callable[[dict], None], Callable[[dict], None]], None]]):
        if code in self.routers:
            raise KeyError(f"route code '{code}' duplicated")
        
        if not hasattr(cb, '__call__'):
            raise KeyError(f"route code '{code}' cb is not callable")
            
        parameters = list(filter(lambda x: x != 'self', get_function_params(cb)))
        param_len = len(parameters)
        if param_len not in (1, 3):
            raise ValueError(f"route code '{code}' cb must have 1 (sync) or 3 (async) parameters, but got {param_len}")
        
        self.routers[code] = cb
        if param_len == 1:
            def go(req, ok, fail):
                try:
                    ok(cb(req))
                except BaseException as e:
                    if isinstance(e, ResponseFail):
                        fail(e.msg, e.res)
                    else:
                        fail(f"request '{code}' failed", None)
            self.routers[code] = go