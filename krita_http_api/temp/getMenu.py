from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time

def get_menu_structure(menu):
    structure = {"title": menu.title(), "actions": []}
    for action in menu.actions():
        if action.menu():  # If the action has a submenu
            structure["actions"].append(get_menu_structure(action.menu()))
        else:
            structure["actions"].append({"title": action.text()})
    return structure

def get_menubar_structure(menubar):
    structure = []
    for action in menubar.actions():
        if action.menu():  # If the action has a submenu
            structure.append(get_menu_structure(action.menu()))
    return structure

x = time.time()
get_menubar_structure(Krita.instance().activeWindow().qwindow().menuBar())
y = time.time()

print(y - x)

