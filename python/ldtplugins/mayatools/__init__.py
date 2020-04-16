"""
.. module:: mayatools
   :synopsis: MayaTools Plugin. Misc viewport utils for Maya

.. moduleauthor:: Ezequiel Mastrasso

"""

import logging
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from yapsy.IPlugin import IPlugin
import ldtmaya
from ldt import context

logger = logging.getLogger(__name__)


class MayaTools(IPlugin):
    """Plug-in for viewport viz utilities Maya."""

    name = "MayaTools Plugin"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        dcc = context.dcc()
        if dcc == 'Maya':
            logger.info('MayaTools loaded')
            import pymel.core as pm
            import ldtmaya
            self.build_ui()
        else:
            logger.warning(
                ' MayaTools  not loaded, dcc libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText(
                'MayaTools\nPlugin not available in this application')

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        self.plugin_layout = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        project_btns_layout = QtWidgets.QHBoxLayout()
        object_btns_layout = QtWidgets.QHBoxLayout()
        selection_layout = QtWidgets.QHBoxLayout()
        wireframe_layout = QtWidgets.QHBoxLayout()
        material_layout = QtWidgets.QHBoxLayout()
        red_text = '#AA0000'

        # wireframe colors
        self.lbl_wireframe = QtWidgets.QLabel("wireframe colors")
        self.btn_wireframe_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project"
        )
        self.btn_wireframe_color_objects = QtWidgets.QPushButton(
            "per Surfacing Object")
        self.btn_wireframe_color_none = QtWidgets.QPushButton("X")
        self.btn_wireframe_color_none.setMaximumWidth(20)
        self.btn_wireframe_color_none.setStyleSheet(
            'QPushButton {color: %s;}' % red_text)
        # material colors
        self.lbl_materials = QtWidgets.QLabel("material colors")
        self.shader_type = QtWidgets.QComboBox()
        self.shader_type.addItem("blinn")
        self.shader_type.addItem("aiStandardSurface")
        self.btn_material_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project")
        self.btn_material_color_objects = QtWidgets.QPushButton(
            "per Surfacing Object")

        # Attach widgets to the main layout
        main_layout.addWidget(self.lbl_wireframe)
        main_layout.addLayout(wireframe_layout)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        wireframe_layout.addWidget(self.btn_wireframe_color_projects)
        wireframe_layout.addWidget(self.btn_wireframe_color_objects)
        wireframe_layout.addWidget(self.btn_wireframe_color_none)
        main_layout.addWidget(self.lbl_materials)
        main_layout.addLayout(material_layout)
        material_layout.addWidget(self.shader_type)
        material_layout.addWidget(self.btn_material_color_projects)
        material_layout.addWidget(self.btn_material_color_objects)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        # Connect buttons signals
        self.btn_wireframe_color_projects.clicked.connect(
            ldtmaya.set_wireframe_colors_per_project
        )
        self.btn_wireframe_color_objects.clicked.connect(
            ldtmaya.set_wireframe_colors_per_object
        )
        self.btn_wireframe_color_none.clicked.connect(
            ldtmaya.set_wifreframe_color_none
        )
        self.btn_material_color_projects.clicked.connect(
            lambda: ldtmaya.set_materials_per_project(self.shader_type.currentText())
        )
        self.btn_material_color_objects.clicked.connect(
            lambda: ldtmaya.set_materials_per_object(self.shader_type.currentText())
        )
