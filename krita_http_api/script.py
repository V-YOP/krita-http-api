# from krita import *
# from datetime import datetime
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *

# from krita import *

# def get_own_methods(obj):
#     meta_object = obj.metaObject()
#     own_methods = []
    
#     # 获取类的自身方法数量
#     own_method_count = meta_object.methodCount()
    
#     # 获取父类的元对象
#     base_meta_object = meta_object.superClass()
#     while base_meta_object:
#         own_method_count -= base_meta_object.methodCount()
#         base_meta_object = base_meta_object.superClass()
    
#     # 过滤并获取自身定义的方法
#     for i in range(own_method_count):
#         method = meta_object.method(i)
#         method_signature = method.methodSignature().data().decode()
#         method_type = method.methodType()
        
#         if method_type == QMetaMethod.Signal:
#             own_methods.append(f"Signal: {method_signature}")
#         elif method_type == QMetaMethod.Slot:
#             own_methods.append(f"Slot: {method_signature}")
#         else:
#             own_methods.append(f"Method: {method_signature}")
    
#     return own_methods

# qdock = next((w for w in Krita.instance().dockers() if w.objectName() == 'sharedtooldocker'), None)
# wobj = qdock.findChild(QWidget,'KritaShape/KisToolBrushoption widget')

# own_methods = get_own_methods(wobj)

# print("Own Methods:")
# for method in own_methods:
#     print(method)

# # meta_object = wobj.metaObject()
# # print(meta_object.className())  # 输出类名

# # # 获取所有方法
# # print("Methods:")
# # for i in range(meta_object.methodCount()):
# #     method = meta_object.method(i)
# #     method_type = method.methodType()
    
# #     # 获取方法名称
# #     method_name = method.methodSignature().data().decode()  # 转换为字符串
    
# #     if method_type == QMetaMethod.Signal:
# #         print("Signal:", method_name)
# #     elif method_type == QMetaMethod.Slot:
# #         print("Slot:", method_name)
# #     else:
# #         print("Method:", method_name)

# # for i in range(meta_object.propertyCount()):
# #     prop = meta_object.property(i)
# #     print(prop.name(), prop.read(wobj))  # 输出属性名称和当前值  \

# print(Krita.instance().krita_i18n('triangle'))


# def f(n: int):
#     if n <= 2:
#         return n
#     return f(n - 1) + f(n - 2)
# print(f(10))


def f(n):
    return (n < 3) * n or f(n - 1) + f(n - 2)
print(f(2))