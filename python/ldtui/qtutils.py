"""
.. module:: qtutils
   :synopsis: small qt utilies and custom widgets.

.. moduleauthor:: Ezequiel Mastrasso

"""

from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

import logging
logger = logging.getLogger(__name__)


def get_folder_path():
    """Gets a folder path from the user"""
    file_dialog = QtWidgets.QFileDialog()
    file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    if file_dialog.exec_():
        path = str(file_dialog.selectedFiles()[0])
        return path
    else:
        return None


class HTabWidget(QtWidgets.QTabBar):
    '''
    QPaint event to draw the QTabWidget titles horizontally
    '''

    def __init__(self, *args, **kwargs):
        self.tabSize = QtCore.QSize(kwargs.pop('width'), kwargs.pop('height'))
        super(HTabWidget, self).__init__(*args, **kwargs)

    def paintEvent(self, event):

        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, QtCore.Qt.AlignVCenter |
                             QtCore.Qt.TextDontClip,
                             self.tabText(index))

    def tabSizeHint(self, index):
        return self.tabSize
