"""
.. module:: ldtmaya
   :synopsis: general maya functions.

.. moduleauthor:: Ezequiel Mastrasso

"""

import ldtcommon
import ldtutils
from ldtcommon import ATTR_SURFACING_PROJECT
from ldtcommon import ATTR_SURFACING_OBJECT
from ldtcommon import ATTR_MATERIAL
from ldtcommon import ATTR_MATERIAL_ASSIGN
from ldtcommon import ATTR_MATERIAL_VP

from ldtui import qtutils
from Qt import QtGui, QtWidgets, QtCore
from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

import os
import sys
import traceback
import random
import logging

import pymel.core as pm
import maya.mel as mel
import maya.cmds as mc

logger = logging.getLogger(__name__)


def surfacingInit():
    """
    Initialize the scene for surfacing projects.

    Creates the surfacing root, an empty surfacing project
    and object, and runs the validation to create and
    connect the partition

    Returns:
        bool. Valid scene.

    """
    root = create_surfacing_root()
    if not root.members:
        surfacing_project = create_surfacing_project("defaultProject")
        create_surfacing_object(surfacing_project, "defaultObject")
    validate_surfacing()


def create_surfacing_root_node():
    """Create projects root node"""
    surfacing_root = pm.createNode(
        "objectSet", name="surfacing_root"
    )
    surfacing_root.setAttr(
        "surfacing_root", "", force=True
    )
    return surfacing_root


def create_surfacing_root():
    """Create projects root if it doesnt exist."""
    if not get_surfacing_root():
        surfacing_root = get_surfacing_root()
        return surfacing_root
    else:
        return get_surfacing_root()


def create_surfacing_project(name=None):
    """
    Creates a surfacing project.

    Kwargs:
        name (str): surfacing project name

    """
    if not name:
        name = "project"
    surfacing_project = pm.createNode(
        "objectSet", name=name
    )
    surfacing_project.setAttr(
        ATTR_SURFACING_PROJECT, "", force=True
    )
    create_surfacing_object(surfacing_project)
    get_surfacing_root().add(surfacing_project)
    update_surfacing_partition()
    return surfacing_project


def create_surfacing_object(project, name=None):
    """
    Creates a surfacing Object under a given project.

    Args:
        project (PyNode): surfacing project

    Kwargs:
        name (str): surfacing object name

    """
    if not name:
        name = "object"
    surfacing_set = pm.createNode(
        "objectSet", name=name
    )
    surfacing_set.setAttr(
        ATTR_SURFACING_OBJECT, "", force=True
    )
    project.add(surfacing_set)

    return surfacing_set


def get_surfacing_root():
    """
    Get the project root node.

    Returns:
        PyNode. Surfacing root node

    Raises:
       Exception.

    """
    objSetLs = [
        item
        for item in pm.ls(type="objectSet")
        if item.hasAttr("surfacing_root")
    ]
    if len(objSetLs) == 0:
        logger.info(
            "surfacing_root node found, creating one"
        )
        return create_surfacing_root_node()
    elif len(objSetLs) > 1:
        raise Exception(
            "More than 1 surfacing_root node found, clean up your scene"
        )
    return objSetLs[0]


def get_surfacing_projects():
    """
    Get all surfacing Projects under the root.

    Returns:
        list. surfacing projects PyNodes list.

    """
    objSetLs = [
        item
        for item in pm.ls(type="objectSet")
        if item.hasAttr(ATTR_SURFACING_PROJECT)
    ]
    return objSetLs


def get_surfacing_project_by_name(name=None):
    """
    Get surfacing Project by name.

    Kwargs:
        name (str): surfacing project name.

    Returns:
        PyNode. Returns first found hit, we are assuming the objectSet name is
        equal to surfacing_project attr value.

    """
    projects_list = get_surfacing_projects()
    for each in projects_list:
        if name == each.name():
            return each
    return None


def get_surfacing_object_by_name(name=None):
    """
    Get surfacing Object by name.

    Kwargs:
        name (str): surfacing object name.

    Returns:
        PyNode. Returns first found hit, we are assuming the objectSet name is
        equal to surfacing_object attr value.

    """
    projects_list = get_surfacing_projects()
    for prj in projects_list:
        objs = get_surfacing_objects(prj)
        for obj in objs:
            if name == obj.name():
                return obj
    return None


def delete_surfacing_project(project):
    """
    Delete a surfacing_project, and its members.

    Args:
        project (PyNode): surfacing project.

    """
    if is_surfacing_project(project):
        pm.delete(project.members())


def get_surfacing_objects(project):
    """
    Get all surfacing Objects under the given surfacing project

    Args:
        project (PyNode): surfacing project

    """
    if is_surfacing_project(project):
        return project.members()
    else:
        return []


def is_surfacing_project(project):
    """
    Check if the node is a surfacing project

    Args:
        project (PyNode): surfacing project

    Returns:
        bool. True if it is.

    """
    if project.hasAttr(ATTR_SURFACING_PROJECT):
        return True
    else:
        return False


def is_surfacing_object(surfacing_object):
    """
    Check if node is surfacing Object

    Args:
        surfacing_object (PyNode): surfacing_object

    """
    if surfacing_object.hasAttr(ATTR_SURFACING_OBJECT):
        return True
    else:
        return False


def remove_surfacing_invalid_members():
    """
    Pops all not-allowd member types from surfacing projects and objects.

    Only Allowed types:
     objectSets (surfacing_projects) inside the surfacing projects root
     objectSets (surfacing_object) inside surfacing projects
     transforms (that have a mesh) inside surfacing_object
    """
    project_root = get_surfacing_root()
    for project in project_root.members():
        if (
            not project.type() == "objectSet"
        ):  # TODO (eze) add check for attr
            project_root.removeMembers([project])
    for project in get_surfacing_projects():
        for object in get_surfacing_objects(
            project
        ):  # TODO (eze) add check for attr
            if not object.type() == "objectSet":
                project.removeMembers([object])
            else:
                for member in object.members():
                    if not member.type() == "transform":
                        logger.info(
                            "removing invalid member: %s"
                            % member
                        )
                        object.removeMembers([member])
                    elif not member.listRelatives(
                        type="mesh"
                    ):
                        logger.info(
                            "removing invalid member: %s"
                            % member
                        )
                        object.removeMembers([member])


def get_mesh_transforms(object_list):
    # TODO move to common
    """
    Get all the mesh shapes transforms.

    Includes all descendants in hierarchy.

    Args:
        object_list (list): PyNode list of nodes.

    """
    shapes_in_hierarchy = pm.listRelatives(
        object_list,
        allDescendents=True,
        path=True,
        f=True,
        type="mesh",
    )
    shapes_transforms = pm.listRelatives(
        shapes_in_hierarchy, p=True, path=True, f=True
    )
    return shapes_transforms


def add_member(surfacing_object, transform):
    # TODO move to common
    """
    Add transform to surfacing Object

    Args:
        surfacing_object (PyNode): surfacing object
        transform (PyNode): transform node

    """
    pm.sets(surfacing_object, transform, fe=True)


def add_mesh_transforms_to_surfacing_object(
    surfacing_object, object_list
):
    """
    Add all mesh shape transforms -and descendants- from the list to a
    surfacing Object.

    Args:
        surfacing_object (PyNode): surfacing object
        object_list (list): object list

    """
    pm.select()
    if is_surfacing_object(surfacing_object):
        for item in object_list:
            # Disconnect the objects from other Surf proj and obj
            for c in item.instObjGroups.listConnections(c=True, p=True):
                if is_surfacing_object(c[1].node()) or is_surfacing_project(c[1].node()):
                    logger.info(
                        "disconnecting from Surf project or obj: %s" % c[1].node()
                    )
                    pm.disconnectAttr("%s"%c[0], "%s"%c[1])
            for transform in get_mesh_transforms(item):
                pm.select(transform)
                add_member(surfacing_object, transform)


def update_surfacing_partition():
    """Recreate the partition node, and reconnects to all the surfacing
    objects objectSets."""
    partitions = [
        item
        for item in pm.ls(type="partition")
        if item.hasAttr("surfacing_partition")
    ]
    for each in partitions:
        logger.info(
            "disconnecting existing partition: %s" % each
        )
        each.sets.disconnect()
        pm.delete(each)
        logger.info("deleted partition")
    surfacing_partition = pm.createNode(
        "partition", name="surfacing_partition"
    )
    logger.info(
        "partition created: %s" % surfacing_partition
    )
    surfacing_partition.setAttr(
        "surfacing_partition", "", force=True
    )
    for project in get_surfacing_projects():
        for object in get_surfacing_objects(project):
            pm.connectAttr(
                "%s.partition" % object,
                surfacing_partition.sets,
                na=True,
            )
            logger.info(
                "partition connected: %s " % object
            )


def remove_invalid_characters():
    """Remove not allowed characters from surfacing projects and names
    like '_'."""
    project_root = get_surfacing_root()
    surfacing_projects = get_surfacing_projects()
    #invalid_character = '_'
    invalid_character = '*'
    for project in surfacing_projects:
        if invalid_character in project.name():
            project.rename(project.name().replace(invalid_character, ''))
            logger.info(
                'Invalid character removed from surfacing_project,'
                'new name: %s' % project)
        for surfacing_object in get_surfacing_objects(project):
            if invalid_character in surfacing_object.name():
                surfacing_object.rename(
                    surfacing_object.name().replace(invalid_character, ''))
                logger.info(
                    'Invalid characters removed from surfacing_object,'
                    'new name: %s' % surfacing_object)


def validate_surfacing():
    """
    Validate the scene.

    Removes invalidad characters and members, updates the partition,
    and mesh attributes.

    """
    remove_invalid_characters()
    remove_surfacing_invalid_members()
    update_surfacing_partition()
    update_surfacing_attributes()


def export_alembic(geo_list, file_path):
    """
    Export alembic file from the object list.

    Args:
        geo_list (list): list of geometry to export
        file_path (str): export file path

    """
    if geo_list and file_path:
        roots = " -root |" + " -root |".join(
            [str(x) for x in geo_list]
        )
        cmd = (
            r'-frameRange 0 0 -uvWrite -dataFormat ogawa '
            r'-userAttrPrefix surfacing' +
            roots + ' -file ' + (file_path)
        )
        logger.info("AbcExport: %s" % cmd)
        mc.AbcExport(j=cmd)
        logger.info(
            "Succesful Alembic export to: %s" % file_path
        )


def merge_surfacing_object_meshes(surfacing_object):
    """
    Merge all the meshs assigned to a surfacing Object.

    Args:
        surfacing_object (PyNode): surfacing object

    Raises:
        BaseException. Could not merge member meshes.

    """
    try:
        members = surfacing_object.members()
        logger.info("Merging members: %s" % members)
        geo_name = "%s_geo" % str(surfacing_object)
        if len(members) > 1:
            geo = pm.polyUnite(*members, n=geo_name)
            return geo[0]
        else:
            logger.info(
                "single object found, skipping merge: %s"
                % members[0]
            )
            members[0].rename(geo_name)
            pm.parent(members[0], world=True)
            return members[0]
    except BaseException:
        logger.error(
            "Could not merge members of: %s"
            % surfacing_object
        )
        return False


def export_surfacing_project(project, subdiv_level=0, single_export=True, folder_path=False):
    """
    Export surfacing Project to Alembic.

    Args:
        project (PyNode): surfacing project

    Kwargs:
        single_export (bool): is single export
        folder_path (str): Export folder path

    """
    current_file = pm.sceneName()
    if single_export:
        save_unsaved_scene_()
    if not folder_path:
        folder_path = qtutils.get_folder_path()
    project_geo_list = []
    if ldtutils.is_directory(folder_path) and is_surfacing_project(project):
        for each in get_surfacing_objects(project):
            merged_geo = merge_surfacing_object_meshes(each)
            if merged_geo:
                project_geo_list.append(merged_geo)
        if project_geo_list:
            if subdiv_level:
                for geo in project_geo_list:
                    logger.info(
                        "subdivision level: %s" % subdiv_level
                    )
                    logger.info(
                        "subdividing merged members: %s"
                        % geo
                    )
                    # -mth 0 -sdt 2 -ovb 1 -ofb 3 -ofc 0 -ost 0 -ocr 0 -dv 3
                    # -bnr 1 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 1
                    # -peh 0 -sl 1 -dpe 1 -ps 0.1 -ro 1 -ch 1
                    pm.polySmooth(
                        geo, mth=0, sdt=2, ovb=1,
                        dv=subdiv_level
                    )
            export_file_path = os.path.join(
                folder_path, str(project) + ".abc"
            )
            export_alembic(project_geo_list, export_file_path)
            export_surfacing_object_dir = os.path.join(
                folder_path, str(project)
            )
            ldtutils.create_directoy(export_surfacing_object_dir)
            for geo in project_geo_list:
                export_root = " -root |" + geo
                export_surfacing_object_path = os.path.join(
                    export_surfacing_object_dir
                    + "/"
                    + geo
                    + ".abc"
                )
                export_alembic(
                    [geo], export_surfacing_object_path
                )

    if single_export:
        pm.openFile(current_file, force=True)


def export_all_surfacing_projects(folder_path=None, subdiv_level=0):
    """
    Export all surfacing Projects.

    Kwargs:
        folder_path (str): folder to export files.

    """
    save_unsaved_scene_()
    if not folder_path:
        folder_path = qtutils.get_folder_path()
    current_file = pm.sceneName()
    for project in get_surfacing_projects():
        export_surfacing_project(
            project, subdiv_level, single_export=False, folder_path=folder_path
        )
    pm.openFile(current_file, force=True)
    return True


def save_unsaved_scene_():
    # TODO move to common
    """Check the scene state, if modified, will ask the user to save it."""
    if unsaved_scene():
        if save_scene_dialog():
            pm.saveFile(force=True)
        else:
            raise ValueError("Unsaved changes")


def update_surfacing_attributes():
    """
    Create attributes on meshes of what surfacing object they are assigned to.

    Adds the attributes to all the shapes transforms assigned to surfacing
    objects. This will be used later for quick shader/material creation and
    assignment.

    """
    for project in get_surfacing_projects():
        project.setAttr(ATTR_SURFACING_PROJECT, project)
        logger.info(
            "Updating attributes for project: %s" % project
        )
        for surfacing_object_set in get_surfacing_objects(project):
            logger.info(
                "\tUpdating attributes for object texture set: %s"
                % surfacing_object_set
            )
            surfacing_object_set.setAttr(
                ATTR_SURFACING_OBJECT, surfacing_object_set
            )
            members = surfacing_object_set.members()
            logger.info(
                "\t\tUpdating attr for meshes: %s" % members
            )
            for member in members:
                member.setAttr(
                    ATTR_SURFACING_PROJECT,
                    project.name(),
                    force=True,
                )
                member.setAttr(
                    ATTR_SURFACING_OBJECT,
                    surfacing_object_set.name(),
                    force=True,
                )


def set_wifreframe_color_black():
    """Set the wireframe color to black in all mesh objects."""
    transforms = pm.ls(type="transform")
    shape_transforms = get_mesh_transforms(transforms)
    for mesh in shape_transforms:
        mesh_shape = mesh.getShape()
        mesh_shape.overrideEnabled.set(1)
        mesh_shape.overrideRGBColors.set(0)
        mesh_shape.overrideColor.set(1)


def set_wifreframe_color_none():
    """Remove the wireframe color in all mesh objects."""
    transforms = pm.ls(type="transform")
    shape_transforms = get_mesh_transforms(transforms)
    for mesh in shape_transforms:
        mesh_shape = mesh.getShape()
        mesh_shape.overrideEnabled.set(0)


def set_wireframe_colors_per_project():
    """
    Set the wireframe color per surfacing project.

    For all meshes, sets it to black to start with,
    this implies that the mesh has not be assigned
    to any surfacing object yet will show black in the VP

    """
    set_wifreframe_color_black()
    projects = get_surfacing_projects()
    for project in projects:
        random.seed(project)
        wire_color = random.randint(1, 31)
        for surfacingObject in get_surfacing_objects(project):
            for mesh in surfacingObject.members():
                mesh_shape = mesh.getShape()
                try:
                    mesh_shape.overrideEnabled.set(1)
                    mesh_shape.overrideRGBColors.set(0)
                    mesh_shape.overrideColor.set(wire_color)
                except:
                    logger.error('Could not set override color for: %s, might '
                                 'belong to a display layer'
                                 % mesh
                                 )


def set_wireframe_colors_per_object():
    """
    Set the wireframe color per surfacing object.

    For all meshes, sets it to black to start with,
    this implies that the mesh has not be assigned
    to any surfacing object yet will show black in the VP

    """
    set_wifreframe_color_black()
    projects = get_surfacing_projects()
    print projects
    for project in projects:
        for surfacingObject in get_surfacing_objects(project):
            for mesh in surfacingObject.members():
                mesh_shape = mesh.getShape()
                try:
                    mesh_shape.overrideEnabled.set(1)
                    mesh_shape.overrideRGBColors.set(1)
                    mesh_shape.overrideColorRGB.set(
                        ldtutils.get_random_color(surfacingObject)
                    )
                except:
                    logger.error('Could not set override color for: %s, might '
                                 'belong to a display layer'
                                 % mesh
                                 )


def set_materials_per_object():
    """Create a material per surfacing project and assigns it"""
    delete_materials()
    projects = get_surfacing_projects()
    for project in projects:
        for obj in get_surfacing_objects(project):
            shader, shading_group = create_shader(
                type='blinn')
            pm.select(obj)
            meshes = pm.ls(sl=True)
            pm.sets(shading_group, forceElement=meshes)
            pm.select(None)
            shader.color.set(
                ldtutils.get_random_color(obj)
            )
            pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL),
                       'obj', force=True)
            pm.setAttr('%s.%s' %
                       (shading_group, ATTR_MATERIAL_ASSIGN), obj.name(), force=True)
            pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL_VP),
                       'color', force=True)


def set_materials_per_project():
    """Create a material per surfacing project and assigns it"""
    delete_materials()
    projects = get_surfacing_projects()
    for project in projects:
        shader, shading_group = create_shader(
            type='blinn')
        pm.select(project)
        meshes = pm.ls(sl=True)
        pm.sets(shading_group, forceElement=meshes)
        pm.select(None)
        shader.color.set(
            ldtutils.get_random_color(project)
        )
        pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL),
                   'project', force=True)
        pm.setAttr('%s.%s' %
                   (shading_group, ATTR_MATERIAL_ASSIGN), project.name(), force=True)
        pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL_VP),
                   'color', force=True)


def delete_materials():
    """delete all material networks that have surfacing attributes"""
    all_shading_groups = pm.ls(type="shadingEngine")
    to_delete = []
    for shading_group in all_shading_groups:
        if pm.hasAttr(shading_group, ATTR_MATERIAL):
            to_delete.append(shading_group)
    pm.delete(to_delete)


def delete_materials_viewport(type=None):
    """
    delete all material networks that have surfacing attributes.

    Kwargs:
        type (str): type of vp material to delete, usually 'color', or 'pattern'

    """
    all_shading_groups = pm.ls(type="shadingEngine")
    to_delete = []
    for shading_group in all_shading_groups:
        if pm.hasAttr(shading_group, ATTR_MATERIAL_VP):
            to_delete.append(shading_group)
    pm.delete(to_delete)


def unsaved_scene():
    """Check for unsaved changes."""
    import maya.cmds as cmds

    return cmds.file(q=True, modified=True)


def save_scene_dialog():
    """
    Ask the user to go ahead save or cancel the operation.

    Returns:
        bool. True is Ok clicked, false otherwise.

    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("Your scene has unsaved changes")
    msg.setInformativeText("")
    msg.setWindowTitle("Warning")
    msg.setDetailedText(
        "This tool will do undoable changes. It requires you to save your scene, and reopen it after its finished"
    )
    msg.setStandardButtons(
        QtWidgets.QMessageBox.Ok
        | QtWidgets.QMessageBox.Cancel
    )
    retval = msg.exec_()
    if retval == QtWidgets.QMessageBox.Ok:
        return True
    else:
        return False


def create_file_node(name=None):
    """
    Create a file node, and its 2dPlacement Node.

    Kwargs:
        name (str): file node name

    Returns:
        PyNode. Image file node

    """
    file_node = pm.shadingNode(
        'file', name=name, asTexture=True, isColorManaged=True)
    placement_name = '%s_place2dfile_nodeture' % name
    placement_node = pm.shadingNode(
        'place2dTexture', name=placement_name, asUtility=True)
    file_node.filterType.set(0)
    pm.connectAttr(placement_node.outUV, file_node.uvCoord)
    pm.connectAttr(placement_node.outUvFilterSize, file_node.uvFilterSize)
    pm.connectAttr(placement_node.coverage, file_node.coverage)
    pm.connectAttr(placement_node.mirrorU, file_node.mirrorU)
    pm.connectAttr(placement_node.mirrorV, file_node.mirrorV)
    pm.connectAttr(placement_node.noiseUV, file_node.noiseUV)
    pm.connectAttr(placement_node.offset, file_node.offset)
    pm.connectAttr(placement_node.repeatUV, file_node.repeatUV)
    pm.connectAttr(placement_node.rotateFrame, file_node.rotateFrame)
    pm.connectAttr(placement_node.rotateUV, file_node.rotateUV)
    pm.connectAttr(placement_node.stagger, file_node.stagger)
    pm.connectAttr(placement_node.translateFrame, file_node.translateFrame)
    pm.connectAttr(placement_node.wrapU, file_node.wrapU)
    pm.connectAttr(placement_node.wrapV, file_node.wrapV)
    return file_node


def create_shader(type='PxrSurface'):
    """
    Create shaders and shading groups.

    Kwargs:
        type (str): type of material shader to create, for ie 'blinn'
        tag (str): tag to set in ATTR_MATERIAL, usually the
                   surfacing project or surfacing object

    Returns:
        tuple. PyNode shader, and PyNode shading_group

    """
    shader, shading_group = pm.createSurfaceShader(type)
    pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL), '', force=True)
    pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL_ASSIGN), '', force=True)
    pm.setAttr('%s.%s' % (shading_group, ATTR_MATERIAL_VP), '', force=True)
    return shader, shading_group


def import_surfacing_textures():
    """
    TODO WE DONT REALLY NEED THIS DONT WE
    TODO THIS IS A WORKING HARDCODED IMPORT, IMPLEMENT CORRECTLY
    Import textures to surfacing objects or projects.

    Kwargs:
        parsed_files (list): list of lucidity parsed files
                             with 'filepath' key
        key (str): surfacing attr to use for import,
                   surfacing project or surfacing object
        shaders (list): a list of shaders, where the keys match
                        the parsed files key to use for import

    """
    import pymel.core as pm
    from ldtcommon import TEXTURE_FILE_PATTERN
    import ldtmaya
    import ldtutils
    import ldttextures
    textures_folder = '/run/media/ezequielm/misc/wrk/current/cabinPixar/textures'
    texture_list = ldtutils.get_files_in_folder(
        textures_folder, recursive=True, pattern='.tex')
    texture_finder = ldttextures.TextureFinder(
        TEXTURE_FILE_PATTERN, texture_list)
    texture_finder.get_channel_plug(texture_list[0])

    for surfPrj in ldtmaya.get_surfacing_projects():
        for surfObj in ldtmaya.get_surfacing_objects(surfPrj):
            # Find texture files with a matching surfacing_project, get udim paths
            texture_files = texture_finder.find_key_values(
                surfacing_project=surfPrj, merge_udims=True)
            if texture_files:
                print surfObj
                # create and assign the material to each surfacing_object
                pm.select(surfObj)
                meshes = pm.ls(sl=True)
                shader, shading_group = ldtmaya.create_shader()
                shader.rename('%s_%s' % (surfObj, 'material'))
                pm.sets(shading_group, forceElement=meshes)
                pm.select(None)
                for texture_file in texture_files:
                    # get the shader plug input, to connect the texture to
                    shader_plug = texture_finder.get_channel_plug(texture_file)
                    if shader_plug:
                        shader_plug = pm.PyNode(
                            '%s.%s' % (shader.name(), shader_plug))
                        # create image nodes
                        file_node = ldtmaya.create_file_node(
                            '%s_%s' % (surfObj, shader_plug))
                        # paths come with 'udim', replac this with the prman <UDIM>
                        file_node.fileTextureName.set(
                            texture_file.replace('udim', '<UDIM>'))
                        pm.setAttr('%s.%s' % (file_node, 'uvTilingMode'), 3)
                        pm.setAttr('%s.%s' %
                                   (file_node, 'alphaIsLuminance'), 1)
                        # TODO Query the shader plug, connect RGB or single channel
                        # TODO if a normal or bump, create the inbetween node
                        # if shader_plug == "normal" or shader_plug == "bump"
                        print "plug %s -->%s" % (texture_file, shader_plug)
                        if len(shader_plug.elements()) == 4:
                            if "bump" in shader_plug.name():
                                bump_node = pm.shadingNode(
                                    'bump2d', asTexture=True)
                                bump_node.rename('%s_%s' % (surfObj, 'bump'))
                                file_node.outAlpha.connect(bump_node.bumpValue)
                                bump_node.outNormal.connect(shader_plug)
                            else:
                                file_node.outColor.connect(shader_plug)
                        else:
                            file_node.outAlpha.connect(shader_plug)
