from typing import Any, Generic, List, TypeVar, Type
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def enum_mapping(cls, enum):
    mapping = {}
    for key in dir(cls):
        value = getattr(cls, key)
        if isinstance(value, enum):
            mapping[key] = value
            mapping[value] = key
    return mapping

T = TypeVar('T')

class QtEnum(Generic[T]):
    """
    Qt 枚举包装类，负责将枚举和其全大写字符串（下划线分割）字符串形式做转换
    """
    def __init__(self, super_class: Any, enum_class: Type[T]) -> None:
        self.__enum_mapping = enum_mapping(super_class, enum_class)
        self.__enum_class = enum_class

    @property
    def raw(self) -> Type[T]:
        return self.__enum_class

    def values(self) -> List[T]:
        return [self.from_str(key) for key in self.__enum_mapping.keys() if isinstance(key, str)]
    
    def str_values(self) -> List[str]:
        return [self.to_str(enum) for enum in self.values()]

    def from_str(self, enum_str: str) -> T:
        """根据枚举实例的字符串形式得到枚举"""
        return self.__enum_class(self.__enum_mapping[enum_str])

    def to_str(self, enum: T) -> str:
        """将枚举实例转换为字符串形式"""
        return self.__enum_mapping[int(enum)]
    
    def list_to_str(self, enums: List[T]) -> List[str]:
        return [self.to_str(enum) for enum in enums]
    
    def list_to_enum(self, enum_strs: List[str]) -> List[T]:
        return [self.from_str(enum_str) for enum_str in enum_strs]

MessageBoxStandardButton = QtEnum(QMessageBox, QMessageBox.StandardButton)
MessageBoxIcon = QtEnum(QMessageBox, QMessageBox.Icon)

if __name__ == "__main__":
    print(MessageBoxStandardButton.values())  # List of ExampleEnum members
    print(MessageBoxStandardButton.str_values())  # List of ExampleEnum members
    print(MessageBoxStandardButton.from_str("Close"))  # ExampleEnum.VALUE_ONE
    print(MessageBoxStandardButton.to_str(QMessageBox.StandardButton.Close))  # "VALUE_TWO"
    print(MessageBoxIcon.values())  # List of ExampleEnum members
    print(MessageBoxIcon.str_values())  # List of ExampleEnum members
    print(MessageBoxIcon.from_str("Question"))  # ExampleEnum.VALUE_ONE
    print(MessageBoxIcon.to_str(QMessageBox.Icon.Question))  # "VALUE_TWO"

# print((QMessageBox.StandardButton.__reduce__(QMessageBox.StandardButton.Close)))

# from PyQt5.QtWidgets import QMessageBox

# # 获取 QMessageBox.StandardButton 中所有枚举值
# enum_values = {name: getattr(QMessageBox.StandardButton, name) for name in dir(QMessageBox.StandardButton) if name.isupper()}


# enum = enum_mapping(QMessageBox, QMessageBox.StandardButton)

# print('Ok = %s' % enum['Ok'])
# print('QMessageBox.Ok = %s' % enum[QMessageBox.Ok])
# print('1024 = %s' % enum[1024])
# print(enum)