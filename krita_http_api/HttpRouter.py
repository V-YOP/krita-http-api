
from .Logger import Logger
from typing import Any, Callable, Union

import inspect

logger = Logger()

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
        logger.info(f"request '{req['code']}, param: {req['param']}")
        self.routers[req['code']](req['param'], ok, fail)

    def add_route(self, code: str, cb: Union[Callable[[Any], Any], Callable[[Any, Callable[[dict], None], Callable[[dict], None]], None]]):
        if code in self.routers:
            raise KeyError(f"route code '{code}' duplicated")
        
        signature = inspect.signature(cb)
        parameters = signature.parameters
        param_len = len(parameters)
        if param_len not in (1, 3):
            raise ValueError(f"cb must have 1 (sync) or 3 (async) parameters")
        
        self.routers[code] = cb
        if param_len == 1:
            def go(req, ok, fail):
                try:
                    ok(cb(req))
                except:
                    fail(f"request {code} failed", None)
            self.routers[code] = go