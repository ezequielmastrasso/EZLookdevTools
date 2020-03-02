"""
.. module:: ldtui
   :synopsis: Main tools UI.

.. moduleauthor:: Ezequiel Mastrasso

"""

from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

import sys
import imp
import os
import logging
from functools import partial
from ldtui import qtutils

import ldt

logger = logging.getLogger(__name__)


class LDTWindow(QMainWindow):
    '''Main Tools UI Window. Loads the plugInfo.plugin_object.plugin_layout
    QWidget from all loaded plugins as tabs'''

    def __init__(self, plugins):
        super(LDTWindow, self).__init__()
        self.setWindowTitle("Look Dev Tool Set")
        self.setGeometry(0, 0, 650, 600)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        tabwidget = QtWidgets.QTabWidget()
        tabwidget.setTabBar(qtutils.HTabWidget(width=150, height=50))
        tabwidget.setTabPosition(QtWidgets.QTabWidget.West)

        # Stylesheet fix for Katana
        # With default colors, the tab text is almost the
        # same as the tab background
        stylesheet = """
        QTabBar::tab:unselected {background: #222222;}
        QTabWidget>QWidget>QWidget{background: #222222;}
        QTabBar::tab:selected {background: #303030;}
        QTabWidget>QWidget>QWidget{background: #303030;}
        """
        tabwidget.setStyleSheet(stylesheet)

        layout.addWidget(tabwidget, 0, 0)
        plugins_ui = {}
        plugins_buttons = {}
        for pluginInfo in plugins.getAllPlugins():
            tabwidget.addTab(
                pluginInfo.plugin_object.plugin_layout,
                pluginInfo.name)
        self.setCentralWidget(tabwidget)
