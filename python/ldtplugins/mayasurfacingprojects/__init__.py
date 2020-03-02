"""
.. module:: mayasurfacingprojects
   :synopsis: MayaSurfacingProjects Plugin. Organizes scenes for export to surfacing.

.. moduleauthor:: Ezequiel Mastrasso

"""

import logging
from yapsy.IPlugin import IPlugin
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
import ldtmaya
from ldt import context

logger = logging.getLogger(__name__)

dcc = context.dcc()
if dcc == 'Maya':
    import pymel.core as pm
    import ldtmaya


class MayaSurfacingProjects(IPlugin):
    """Plug-in to Organize meshes for surfacing in Maya."""

    name = "MayaSurfacingProjects Plugin"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        dcc = context.dcc()
        if dcc == 'Maya':
            logger.info('MayaSurfacingProjects loaded')
            self.build_ui()
        else:
            logger.warning(
                'MayaSurfacingProjects  not loaded, dcc libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText(
                'MayaSurfacingProjects\nPlugin not available in this application')

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        self.plugin_layout = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        project_layout = QtWidgets.QHBoxLayout()
        project_btns_layout = QtWidgets.QVBoxLayout()
        project_btns_layout.setAlignment(QtCore.Qt.AlignCenter)
        object_layout = QtWidgets.QHBoxLayout()
        object_btns_layout = QtWidgets.QVBoxLayout()
        object_btns_layout.setAlignment(QtCore.Qt.AlignCenter)
        selection_layout = QtWidgets.QHBoxLayout()
        wireframe_layout = QtWidgets.QHBoxLayout()
        material_layout = QtWidgets.QHBoxLayout()
        red_text = '#AA0000'

        # Create UI widgets
        self.refresh = QtWidgets.QPushButton("refresh")
        self.sync_selection = QtWidgets.QCheckBox("Sync object set selection")
        self.expand_selection = QtWidgets.QCheckBox(
            "expand selection to members")

        self.project_new_btn = QtWidgets.QPushButton("new texture project")
        self.project_delete_btn = QtWidgets.QPushButton("X")
        self.project_delete_btn.setStyleSheet(
            'QPushButton {color: %s;}' % red_text)

        self.list_projects = QtWidgets.QListWidget()
        self.list_projects.setSortingEnabled(True)

        self.btn_new_texture_object = QtWidgets.QPushButton(
            "new texture object")
        self.btn_delete_texture_object = QtWidgets.QPushButton("X")
        self.btn_delete_texture_object.setStyleSheet(
            'QPushButton {color: %s;}' % red_text)
        self.btn_add_to_surfacing_object = QtWidgets.QPushButton(
            "add selected"
        )

        self.list_texture_objects = QtWidgets.QListWidget()
        self.list_texture_objects.setSortingEnabled(True)
        self.lbl_validate_scene = QtWidgets.QLabel("validation")
        self.btn_validate_scene = QtWidgets.QPushButton("check scene")
        self.btn_validate_scene.setToolTip('Pops any non-allow types from surfacing\n'
                                           'projects and objects. And makes sure meshes are\n'
                                           'in one and only one surfacing object')

        self.lbl_export = QtWidgets.QLabel("Export")
        self.lbl_subdiv_level = QtWidgets.QLabel("subdiv level")
        self.cmb_export_subdiv = QtWidgets.QComboBox()
        self.cmb_export_subdiv.addItem('0')
        self.cmb_export_subdiv.addItem('1')
        self.cmb_export_subdiv.addItem('2')

        self.btn_export_project = QtWidgets.QPushButton("Selected Project")
        self.btn_export_all = QtWidgets.QPushButton("All Projects")

        # Attach widgets to the main layout
        main_layout.addWidget(self.refresh)
        main_layout.addLayout(selection_layout)
        selection_layout.addWidget(self.sync_selection)
        selection_layout.addWidget(self.expand_selection)
        main_layout.addLayout(project_layout)
        project_layout.addWidget(self.list_projects)
        project_layout.addLayout(project_btns_layout)
        project_btns_layout.addWidget(self.project_new_btn)
        project_btns_layout.addWidget(self.project_delete_btn)
        main_layout.addLayout(object_layout)
        object_layout.addWidget(self.list_texture_objects)
        object_layout.addLayout(object_btns_layout)
        object_btns_layout.addWidget(self.btn_new_texture_object)
        object_btns_layout.addWidget(self.btn_add_to_surfacing_object)
        object_btns_layout.addWidget(self.btn_delete_texture_object)
        main_layout.addWidget(self.lbl_validate_scene)
        main_layout.addWidget(self.btn_validate_scene)
        main_layout.addWidget(self.lbl_export)
        main_layout.addWidget(self.lbl_subdiv_level)
        main_layout.addWidget(self.cmb_export_subdiv)
        main_layout.addWidget(self.btn_export_project)
        main_layout.addWidget(self.btn_export_all)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        # Connect buttons signals
        self.refresh.clicked.connect(self.update_ui_projects)
        self.project_new_btn.clicked.connect(self.create_project)
        self.project_delete_btn.clicked.connect(self.delete_project)
        self.list_projects.itemClicked.connect(self.update_ui_texture_objects)
        self.list_projects.itemDoubleClicked.connect(self.editItem)
        self.btn_new_texture_object.clicked.connect(
            self.create_surfacing_object)
        self.btn_delete_texture_object.clicked.connect(
            self.delete_texture_object)
        self.btn_add_to_surfacing_object.clicked.connect(
            self.add_to_surfacing_object)
        self.btn_validate_scene.clicked.connect(self.validate_scene)
        self.list_texture_objects.itemClicked.connect(
            self.select_surfacing_object)
        self.list_texture_objects.itemDoubleClicked.connect(self.editItem)
        self.btn_export_project.clicked.connect(self.export_project)
        self.btn_export_all.clicked.connect(self.export_all_projects)

    def editItem(self, item):
        """Edit list item name."""
        item_object_set = pm.PyNode(str(item.text()))
        text, okPressed = QtWidgets.QInputDialog.getText(
            self.plugin_layout, "", "rename to:", QtWidgets.QLineEdit.Normal, str(
                item.text())
        )
        if okPressed and text != "":
            logger.info("renaming objsetSet %s to %s" % (item.text(), text))
            try:
                pm.rename(item_object_set, text)
            except:
                pass
            finally:
                self.update_ui_projects()

    def delete_project(self):
        """Delete a surfacing project."""
        selected_project = pm.PyNode(self.list_projects.currentItem().text())
        ldtmaya.delete_surfacing_project(selected_project)
        self.update_ui_projects()

    def select_surfacing_object(self, item):
        """Select surfacing object on the scene."""
        selected_texture_object = pm.PyNode(str(item.text()))
        if self.sync_selection.isChecked():
            pm.select(selected_texture_object, ne=True)
            if self.expand_selection.isChecked():
                pm.select(selected_texture_object)

    def create_project(self):
        """Create a surfacing project and update the UI."""
        project = ldtmaya.create_surfacing_project()
        self.update_ui_projects()

    def create_surfacing_object(self):
        """Create a new surfacing object."""
        if self.list_projects.currentItem():
            selected_project = pm.PyNode(
                self.list_projects.currentItem().text())
            pm.select(selected_project)
            ldtmaya.create_surfacing_object(selected_project)
            self.update_ui_texture_objects(self.list_projects.currentItem())

    def delete_texture_object(self):
        """Delete surfacing object."""
        if self.list_texture_objects.currentItem():
            selected_object = pm.PyNode(
                self.list_texture_objects.currentItem().text())
            if selected_object and ldtmaya.is_surfacing_object(selected_object):
                pm.delete(selected_object)
                self.update_ui_projects()

    def update_ui_projects(self):
        """Update the list of surfacing projects."""
        root = ldtmaya.get_surfacing_root()
        # update_lists
        projects = ldtmaya.get_surfacing_projects()
        self.list_projects.clear()
        for each in projects:
            self.list_projects.addItem(str(each))
        self.list_texture_objects.clear()

    def update_ui_texture_objects(self, item):
        """Update the list of surfacing objects in the selected surfacing project."""
        selected_project = pm.PyNode(str(item.text()))
        texture_objects = ldtmaya.get_surfacing_objects(
            selected_project)
        self.list_texture_objects.clear()
        for each in texture_objects:
            self.list_texture_objects.addItem(str(each))
        if self.sync_selection.isChecked():
            pm.select(selected_project, ne=True)

    def add_to_surfacing_object(self):
        """Add maya selection to currently selected surfacing object"""
        selected_texture_object = pm.PyNode(
            str(self.list_texture_objects.currentItem().text())
        )
        if selected_texture_object:
            ldtmaya.add_mesh_transforms_to_surfacing_object(
                pm.PyNode(selected_texture_object), pm.ls(sl=True)
            )

    def validate_scene(self):
        """Scene validation and update UI."""
        ldtmaya.validate_surfacing()
        self.update_ui_projects()

    def export_project(self):
        """Export single surfacing project."""
        selected_project = pm.PyNode(
            str(self.list_projects.currentItem().text()))
        if selected_project:
            # TODO: Sanitize QLineedit text
            ldtmaya.export_surfacing_project(
                selected_project, subdiv_level=int(self.cmb_export_subdiv.currentText()))

    def export_all_projects(self):
        """Export all surfacing projects."""
        # TODO: Sanitize QLineedit text
        ldtmaya.export_all_surfacing_projects(
            subdiv_level=int(self.cmb_export_subdiv.currentText()))
