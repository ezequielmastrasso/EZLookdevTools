from ldtcommon import ATTR_SURFACING_PROJECT
from ldtcommon import ATTR_SURFACING_OBJECT
from ldtcommon import TEXTURE_FILE_PATTERN
from ldt import context
from ldtui import qtutils
"""
.. module:: Maya import material
   :synopsis: MayaTextureImport Plugin. Imports textureSets to maya Surfacing Projects

.. moduleauthor:: Ezequiel Mastrasso

"""
import os
import logging
from functools import partial
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from yapsy.IPlugin import IPlugin

import ldtutils
import ldtmaya
import ldttextures

logger = logging.getLogger(__name__)


class MayaTextureImport(IPlugin):
    """Plug-in to Import textures to surfacing projects and surfacing objects."""

    name = "MayaTextureImport Plugin"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        dcc = context.dcc()
        if dcc == 'Maya':
            logger.info('MayaTextureImport loaded')
            import pymel.core as pm
            import ldtmaya
            self.build_ui()
        else:
            logger.warning(
                'MayaTextureImport  not loaded, dcc libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText(
                'MayaTextureImport\nPlugin not available in this application')

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        self.plugin_layout = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()

        self.lbl_extension = QtWidgets.QLabel('Find files with pattern')
        self.ln_pattern = QtWidgets.QLineEdit('.tex')
        self.btn_search_files = QtWidgets.QPushButton(
            "Search files in folder"
        )
        self.form_widget = QtWidgets.QTableWidget(0, 2)
        self.form_widget.setWordWrap(True)
        # col_headers = ['filepath', 'import', 'Select in Maya']
        col_headers = ['filepath', 'import']
        self.form_widget.setHorizontalHeaderLabels(col_headers)
        self.form_widget.setRowCount(0)
        self.form_widget.setColumnWidth(0, 300)

        main_layout = QtWidgets.QVBoxLayout()

        # Attach widgets to the main layout
        main_layout.addWidget(self.lbl_extension)
        main_layout.addWidget(self.ln_pattern)

        main_layout.addWidget(self.btn_search_files)
        main_layout.addWidget(self.form_widget)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        self.btn_search_files.clicked.connect(
            self.load_textures
        )

    def load_textures(self):
        """Load textures and populates form."""
        search_folder = qtutils.get_folder_path()
        if search_folder:
            logger.info('Search folder: %s' % search_folder)
            file_list = ldtutils.get_files_in_folder(
                search_folder, recursive=True, pattern=self.ln_pattern.text())
        self.populate_form(file_list)

    def populate_form(self, file_list):
        """
        Populate form with texture lucidity parsed files.

        Args:
            file_templates (list): A list of lucidity parsed files, with file_path key added.

        """
        texture_finder = ldttextures.TextureFinder(file_list)
        udim_file_list = texture_finder.merge_udims()
        self.form_widget.setRowCount(len(udim_file_list))
        buttons = {}
        for num, file_path in enumerate(udim_file_list):
            self.form_widget.setCellWidget(
                num, 0, QtWidgets.QLabel(file_path))
            buttons[num] = QtWidgets.QPushButton('import')
            self.form_widget.setCellWidget(
                num, 1, buttons[num])
            # TODO if there is a file node in the scene with
            # the same path, add the option to select it.
            # self.form_widget.setCellWidget(
            #    num, 2, QtWidgets.QPushButton('select'))
            buttons[num].clicked.connect(
                lambda x=file_path: self.import_texture(x))

    def import_texture(self, file_path):
        """ Creates a maya file node with the given file_path."""
        file_path = file_path.replace('udim', '<UDIM>')
        file_node = ldtmaya.create_file_node(name=os.path.basename(file_path))
        file_node.fileTextureName.set(file_path)
