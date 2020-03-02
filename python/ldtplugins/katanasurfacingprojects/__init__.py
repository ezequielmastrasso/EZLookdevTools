"""
.. module:: katanasurfacing projects
   :synopsis: KatanaSurfacingProjects Plug-in. Katana surfacing projects Tools.

.. moduleauthor:: Ezequiel Mastrasso

"""

import logging
from functools import partial

from yapsy.IPlugin import IPlugin
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from ldt import context

logger = logging.getLogger(__name__)


class KatanaSurfacingProjects(IPlugin):
    """Plug-in to build katana collections and materials for surfacing projects."""
    name = "Katana Surfacing Projects"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        dcc = context.dcc()
        if dcc == 'Katana':
            import ldtkatana
            logger.info('KatanaSurfacingProjects loaded')
            self.build_ui()
        else:
            logger.warning(
                'KatanaSurfacingProjects  not loaded, dcc libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText(
                'KatanaSurfacingProjects\nPlugin not available in this application')

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        self.plugin_layout = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        wireframe_layout = QtWidgets.QHBoxLayout()
        material_layout = QtWidgets.QHBoxLayout()
        viewport_layout = QtWidgets.QHBoxLayout()
        custom_atttribute_layout = QtWidgets.QHBoxLayout()
        red_text = '#AA0000'

        # Create UI widgets
        self.lbl_note = QtWidgets.QLabel(
            "This tools require a nodegraph node to be selected\nfrom where to cook the scene\n")
        # collections
        self.lbl_collections = QtWidgets.QLabel("Collections Create")
        self.btn_collections_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project"
        )
        self.btn_collections_color_objects = QtWidgets.QPushButton(
            "per Surfacing Object")
        # materials
        self.lbl_materials = QtWidgets.QLabel("Materials Create")
        self.btn_material_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project")
        self.btn_material_color_objects = QtWidgets.QPushButton(
            "per Surfacing Object")
        # viewport
        self.lbl_viewport = QtWidgets.QLabel("Viewport Colors")
        self.btn_viewport_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project")
        self.btn_viewport_color_objects = QtWidgets.QPushButton(
            "per Surfacing Object")
        # custom attribute
        self.lbl_custom_attribute = QtWidgets.QLabel(
            "Collection Create - Custom Attribute")

        # Attach widgets to the main layout
        main_layout.addWidget(self.lbl_note)
        main_layout.addWidget(self.lbl_collections)
        main_layout.addLayout(wireframe_layout)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        wireframe_layout.addWidget(self.btn_collections_color_projects)
        wireframe_layout.addWidget(self.btn_collections_color_objects)
        main_layout.addWidget(self.lbl_materials)
        main_layout.addLayout(material_layout)
        material_layout.addWidget(self.btn_material_color_projects)
        material_layout.addWidget(self.btn_material_color_objects)
        main_layout.addWidget(self.lbl_viewport)
        main_layout.addLayout(viewport_layout)
        viewport_layout.addWidget(self.btn_viewport_color_projects)
        viewport_layout.addWidget(self.btn_viewport_color_objects)

        main_layout.addWidget(self.lbl_custom_attribute)
        main_layout.addLayout(custom_atttribute_layout)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        # Connect buttons signals
        self.btn_collections_color_projects.clicked.connect(
            partial(ldtkatana.create_collections,
                    "geometry.arbitrary.surfacing_project")
        )

        self.btn_collections_color_objects.clicked.connect(
            partial(ldtkatana.create_collections,
                    "geometry.arbitrary.surfacing_object")
        )
        self.btn_material_color_projects.clicked.connect(
            partial(ldtkatana.create_materials,
                    "geometry.arbitrary.surfacing_project")
        )
        self.btn_material_color_objects.clicked.connect(
            partial(ldtkatana.create_materials,
                    "geometry.arbitrary.surfacing_object")
        )
        self.btn_viewport_color_projects.clicked.connect(
            partial(ldtkatana.create_viewer_settings,
                    "geometry.arbitrary.surfacing_project")
        )
        self.btn_viewport_color_objects.clicked.connect(
            partial(ldtkatana.create_viewer_settings,
                    "geometry.arbitrary.surfacing_object")
        )
