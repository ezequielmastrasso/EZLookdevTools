"""
.. module:: ldtutils
   :synopsis: general non dcc specific utils.

.. moduleauthor:: Ezequiel Mastrasso

"""
from ldtcommon import CONFIG_MATERIALS_JSON
from ldtcommon import TEXTURE_CHANNEL_MATCHING_RATIO
from ldtcommon import TEXTURE_MATCHING_RATIO
from fuzzywuzzy import fuzz
import subprocess
import multiprocessing
import sys
import json
import logging
import os
import random
import lucidity

logger = logging.getLogger(__name__)


def create_commands(texture_mapping):
    default_command = "maya -batch -file someMayaFile.mb -command "
    commands = []
    for key, value in texture_mapping:
        dir, filename = os.path.split(key)
        filename, ext = os.path.splitext(filename)
        filename = os.path.join(dir, filename + "WithTexture." + ext)
        commands.append("".format(default_command, "abc_file",
                                  key, "texture", value, "file -save ", filename))
    return commands


def launch_function(func, args):
    commands = create_commands(args)
    launch_multiprocess(launch_subprocess, commands)


def launch_subprocess(command):
    try:
        subprocess_output = subprocess.check_output(command)
        logger.info("Subprocess launched\t{out}\nrunning the command\t{command}",
                    out=subprocess_output,
                    command=command)
    except subprocess.CalledProcessError as e:
        logger.exception(
            "Error while trying to launch subprocess: {}".format(e.output))
        raise
    return command


def launch_multiprocess(function, args):
    """
    :param function: Function to be called inside the multiprocess -- Takes only 1 arg
    :param args: list/tuple of arguments for above function
    :return:
    """
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=int(multiprocessing.cpu_count()/2))
    logger.debug("Pool created")
    try:
        pool_process = pool.map_async(function, (args))
    except Exception as e:
        msg = "Error while trying to launch process in pool: {}".format(e)
        logger.exception(msg)
        raise
    finally:
        pool.close()
        pool.join()
    try:
        logger.info("output from the process: {pool_out}",
                    out=pool_process.successful())
        return 0
    except AssertionError:
        logger.exception("Couldn't communicate with the process poll created; \
        No output from processes fetched")
        return 1


def map_textures_to_alembic(texture_mapping):
    launch_subprocess(command)


def load_json(file_path):
    """
    Load a json an returns a dict.

    Args:
        file_path (str): Json file path to open.

    """
    with open(file_path) as handle:
        dictdump = json.loads(handle.read())
    return dictdump


def save_json(file_path, data):
    """
    Dump a dict into a json file.

    Args:
        file_path (str): Json file path to save.
        data (dict): Data to save into the json file.

    """
    # TODO (eze)
    pass


def get_random_color(seed):
    """
    Return a random color using a seed.

    Used by all material creating, and viewport color functions
    that do not use textures, to have a common color accross dccs

    Args:
        seed (str):

    Returns:
        tuple, R,G,B colors.

    """
    random.seed(seed + "_r")
    color_red = random.uniform(0, 1)
    random.seed(seed + "_g")
    color_green = random.uniform(0, 1)
    random.seed(seed + "_b")
    color_blue = random.uniform(0, 1)
    return color_red, color_green, color_blue


def create_directoy(path):
    """
    Create a folder.

    Args:
        path (str): Directory path to create.

    """
    os.mkdir(path)
    logger.info("Directory created: %s" % path)


def is_directory(path):
    """
    Check if the given path exists, and is a directory.

    Args:
        path (str): Directory to check.

    """
    if os.path.exists(path) and os.path.isdir(path):
        return True
    else:
        return False


def get_files_in_folder(path, recursive=False, pattern=None):
    """
    Search files in a folder.

    Args:
        path (str): Path to search.

    Kwards:
        recursive (bool): Search files recursively in folder.
        pattern (str): pattern to match, for ie '.exr'.

    Returns:
        array. File list

    """
    logger.info("Searching for files in: %s" % path)
    logger.info("Searching options: Recursive %s, pattern: %s" %
                (recursive, pattern))
    file_list = []
    for path, subdirs, files in os.walk(path):
        for file in files:
            # skip .mayaswatchs stuff
            if ".maya" not in file:
                if pattern:
                    if pattern in file:
                        file_list.append(os.path.join(path, file))
                        logger.debug(
                            "File with pattern found, added to the list: %s" % file)
                else:
                    file_list.append(os.path.join(path, file))
                    logger.debug("File added to the list: %s" % file)
        if not recursive:
            break
    return file_list


def string_matching_ratio(stringA, stringB):
    """
    Compare two strings and returns a fuzzy string matching ratio.

    In general ratio, partial_ratio, token_sort_ratio
    and token_set_ratio did not give different 
    results given that we are comparin a single.
    TODO: Try bitap algorithm for fuzzy matching, partial substring
    matching might be better for our cases.
    Different channels fuzzy ratio comparission
        ('baseColor','diffusecolor')        =   67
        ('base','diffusecolor')             =   25
        ('specular','specularColor')        =   76
        ('specular','specularcolor')        =   76
        ('specular_color', 'specular_bump') =   67
        ('coat_color', 'coat_ior')          =   78
        ('secondary_specular_color', 'secondary_specular_ior')  =   91
        ('subsurface_weight', 'subsurface_Color')   =  67
        ('emission', 'emission_weight')     =   70
    Same channel diferent naming ratio comparission
        ('diffuse_weight','diffuseGain')    =   64

    Args:
        stringA (str): string to compare against.
        stringB (str): string to compare.

    Returns:
        int. Ratio, from 0 to 100 according to fuzzy matching.

    """
    return fuzz.token_set_ratio(stringA, stringB)


def get_config_materials():
    """
    Gets the CONFIG_MATERIALS_JSON as a dict

    Returns:
        dict. CONFIG_MATERIALS_JSON

    """
    return load_json(CONFIG_MATERIALS_JSON)
