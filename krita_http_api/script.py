from krita import *
from datetime import datetime

def printNode(node: Node, level = 0):
    print(level * ' ' + node.name() + '  ' + f"{node.alphaLocked()=}, {node.collapsed()=}, {node.colorDepth()=}, {node.colorLabel()=}, {node.dynamicPropertyNames()=} {node.hasExtents()=}, {node.metaObject().className()=}, {node.metaObject().propertyCount()=} {node.dynamicPropertyNames()} {node.objectName()=}, {node.metaObject().method=}" )
    for child in reversed(node.childNodes()):
        printNode(child, level + 2)

printNode(Krita.instance().activeDocument().rootNode())

lst = Krita.instance().activeDocument().rootNode().childNodes()
ref = lst[-1]

print(f"{ref.type()=} {ref.layerStyleToAsl()=} {ref.visible()=} {ref.dumpObjectInfo()} {ref.parent()=}")

