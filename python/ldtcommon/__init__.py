"""
.. module:: ldtcommon
   :synopsis: Constants and templates non dcc specific used in other packages.

.. moduleauthor:: Ezequiel Mastrasso

"""

import lucidity
import logging
import os

logger = logging.getLogger(__name__)

LOOKDEVTOOLS_FOLDER = os.environ['LOOKDEVTOOLS']

#: Attributes for tagging meshes for surfacing and texture-to-mesh matching
ATTR_SURFACING_PROJECT = "surfacing_project"
ATTR_SURFACING_OBJECT = "surfacing_object"

#: Attribute for tagging Materials. Values: name of assigned project or object
ATTR_MATERIAL = "surfacing_material"
#: Attribute for tagging material assignmnents. Values: 'project' or 'object']
ATTR_MATERIAL_ASSIGN = "surfacing_assign"
#: Attribute for tagging viewport material. Values: 'color' or 'pattern']
ATTR_MATERIAL_VP = "surfacing_vp"

#: Global string matching ratios to compare strings against lucidity parsed files.
#: Notice that the ratio constant should be high enough,
TEXTURE_MATCHING_RATIO = 90
TEXTURE_CHANNEL_MATCHING_RATIO = 90

#: Texture file template, ANCHOR RIGHT
TEXTURE_FILE_PATTERN = '{surfacing_project}_{surfacing_object}_{channel}_{colorspace}.{udim}.{extension}'

#: Default shader node to use
DEFAULT_SHADER = 'PxrSurface'

#: Materials json Config, contains texture name mappings to shader plugs
CONFIG_MATERIALS_JSON = os.path.join(
    os.environ['LOOKDEVTOOLS'], 'python', 'ldtconfig', 'materials.json')


def texture_file_template(custom_pattern=None):
    """
    Get a lucidity Template object using a custom template.

    Kwargs:
       custom_pattern (str):  Custom lucidity file pattern.

    Returns:
        lucity.Template object with the custom partern

    """
    logger.info('Loading lucidity with:\n    %s' % custom_pattern)
    texture_file_template = lucidity.Template(
        'textureset_element',
        custom_pattern,
        anchor=lucidity.Template.ANCHOR_END
        # TODO (Eze) Add STRICT?
    )
    return texture_file_template
