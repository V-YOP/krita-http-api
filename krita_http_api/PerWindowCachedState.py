from krita import *
from typing import TypeVar, Callable, Generic

T = TypeVar('T')

class PerWindowCachedState(Generic[T]):
    def __init__(self, state_getter: Callable[[Window], T]) -> None:
        self.__state_getter = state_getter
        self.cache: dict[str, T] = {}
    
    def __window_id(self, window: Window):
        return window.qwindow().objectName()
    def get(self, window: Window) -> T:
        id = self.__window_id(window)
        if id in self.cache:
            return self.cache[id]
        self.cache[id] = self.__state_getter(window)
        return self.cache[id]
    
    def clear(self, window: Window = None):
        if window is None:
            self.cache = {}
            return
        id = self.__window_id(window)
        del self.cache[id]

    