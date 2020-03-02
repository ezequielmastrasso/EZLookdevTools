"""
.. module:: txmake
   :synopsis: TxMake Plugin. Convert textures to tex.

.. moduleauthor:: Ezequiel Mastrasso

"""

import os
import logging

from yapsy.IPlugin import IPlugin

import ldtprman
import ldtutils
from ldtui import qtutils
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

logger = logging.getLogger(__name__)


class TxMake(IPlugin):
    """Plug-in to Convert textures to tex."""

    name = "TxMake Plugin"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        # Non DCC specific
        dcc = True
        logger.info('TxMake loaded')
        self.build_ui()

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        # TODO (eze): add a QtLineEdit where to add the arguments list
        self.plugin_layout = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        txmake_layout = QtWidgets.QVBoxLayout()

        # Create UI widgets
        # txmake colors
        self.lbl_txmake = QtWidgets.QLabel(
            "Convert Textures to .tex renderman format")
        self.lbl_extension = QtWidgets.QLabel("file extension search")
        self.line_extension = QtWidgets.QLineEdit(".exr")
        self.lbl_arguments = QtWidgets.QLabel("comma separated arguments")
        self.line_arguments = QtWidgets.QLineEdit("")
        self.cbox_recursive = QtWidgets.QCheckBox("search subdirectories")
        self.btn_txmake = QtWidgets.QPushButton(
            "Select a folder"
        )

        # Attach widgets to the main layout
        main_layout.addWidget(self.lbl_txmake)
        main_layout.addLayout(txmake_layout)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        txmake_layout.addWidget(self.lbl_extension)
        txmake_layout.addWidget(self.line_extension)
        txmake_layout.addWidget(self.lbl_arguments)
        txmake_layout.addWidget(self.line_arguments)
        txmake_layout.addWidget(self.cbox_recursive)
        txmake_layout.addWidget(self.btn_txmake)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        # Connect buttons signals
        self.btn_txmake.clicked.connect(
            self.run
        )

    def run(self):
        """Convert textures."""
        # TODO (eze) use job dispatcher from Anant when ready
        folder_path = qtutils.get_folder_path()
        file_list = ldtutils.get_files_in_folder(folder_path,
                                                 recursive=self.cbox_recursive.checkState(),
                                                 pattern=self.line_extension.text()
                                                 )
        ldtprman.convert_to_tx(file_list)
