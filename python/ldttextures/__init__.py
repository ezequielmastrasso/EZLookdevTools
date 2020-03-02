"""
.. module:: ldtextures
   :synopsis: Texture utilities to manage and find texture files.

.. moduleauthor:: Ezequiel Mastrasso

"""
import re
import logging

import ldtutils
import ldtcommon
from ldtcommon import TEXTURE_CHANNEL_MATCHING_RATIO

logger = logging.getLogger(__name__)


class TextureFinder():
    """
    Search files in a folder.

    Args:
        template (str): lucidity like file template.
        file_list (list): A list of file paths

    """
    texture_template = None
    template = None
    file_list = None

    def __init__(self, file_list, template=None):
        """Initilize the TextureFinder."""
        if template:
            self.texture_template = template
            self.template = ldtcommon.texture_file_template(
                template)
        self.file_list = file_list

    def parse(self, file_path):
        """
        Parse a file path through the Class lucidity template.

        Args:
            file_path (str): a path to a file.

        Returns:
            dict. file path tokens from template

        """
        if not self.texture_template:
            logger.error('Skipping parsing, no template supplied!')
            return {}
        try:
            tokens = self.template.parse(file_path)
            return tokens
        except:
            logger.warning('File did not match template = %s' % file_path)
            return {}

    def find_key_values(self, merge_udims=False, **kwargs):
        """

        Search for key value pairs, that match file template tokens.

        KWargs:
            merge_udims (bool): if true, returns "<udim>" paths.
            **kwargs: key value pairs, to search

        returns:
            list. List of files that match the search criteria

        """
        if not self.texture_template:
            logger.error('Skipping finding keys, no template supplied!')
            return []

        key_count = len(kwargs.items())
        matchs = []
        for file_path in self.file_list:
            tokens = self.parse(file_path)
            match_count = 0
            for key, value in kwargs.items():
                if key in tokens.keys():
                    if tokens[key] == str(value):
                        # Count matchs
                        match_count = match_count + 1
            # if matchs == keywords count we found all keys/values
            if key_count == match_count:
                matchs.append(file_path)
        if merge_udims:
            return self.merge_udims(matchs)
        else:
            return matchs

    @staticmethod
    def get_udim(file_path):
        """
        Gets the udim part of a file.

        Searches the file name for numbers between 1000 and 2000,
        delimited by "_" or ".".

        Args:
            file_path (str): a file path.

        Returns:
            int: udim

        """
        sequences = re.split("[._]+", file_path)
        udim = None
        for s in sequences:
            try:
                udim = int(s)
            except:
                pass
        if udim > 1000 and udim < 2000:
            return udim
        else:
            return None

    def merge_udims(self, file_list=None):
        """
        TODO make template agnostic, use get_udim instead, make static
        Return a file_list, with the {udim} part replaced by '<udim>'.

        Duplicates are skipped. Optionaly, it can be given an file_list.
        This is handy for cases where you don't want to use the whole
        list. But for ie: a file_list returned by find_key_values().

        Kwargs:
            file_list (list): A list of file paths.

        returns:
            list. A list of files merged by udim.

        """
        # If a file_list is not provided, use self.file_list
        if file_list is None:
            file_list = self.file_list
        udim_file_list = []
        for file_path in file_list:
            udim = self.get_udim(file_path)
            udim_file_path = file_path.replace(str(udim), 'udim')
            if udim_file_path not in udim_file_list:
                udim_file_list.append(udim_file_path)
        return udim_file_list

    def get_token(self, file_path, token=None):
        """

        Parse the file_path with the template, and return the give key value

        Args:
            file_path (str): a file path.
            token (str): dictionary key to get.

        Returns:
            string: Value of the key (token) from the template parsed file.

        """
        return self.parse(file_path)[token]

    def get_channel_plug(self, file_path, shader_type='PxrSurface'):
        """

        Match the file channel name with a shader plug.

        Loads the material json from ldtconfig folder, and tries to find
        a close match using fuzzy wuzz

        Args:
            file_path (str): a file path

        Kargs:
            shader_type (str): A shader node name to find in the material json

        Returns:
            string: The name of the shader plug matched 

        """
        # TODO make it iterate the material_mapping keys and find .max()
        # instead of the first hit
        materials_config = ldtutils.get_config_materials()
        logger.debug('TEXTURE_CHANNEL_MATCHING_RATIO = %s' %
                     TEXTURE_CHANNEL_MATCHING_RATIO)
        tokens = self.parse(file_path)
        channel = tokens['channel']
        for key in materials_config['material_mapping'][shader_type]:
            ratio = ldtutils.string_matching_ratio(channel, key)
            logger.debug('Comparing %s with %s. Ratio is %s' %
                         (channel, key, ratio))
            if ratio > TEXTURE_CHANNEL_MATCHING_RATIO:
                logger.debug('Ratio above threshold found. Matched "%s" with "%s".' %
                             (channel, key))
                return materials_config['material_mapping']['PxrSurface'][key]
        logger.debug(
            'Could not find a match above the ratio for %s' % channel)
        return
