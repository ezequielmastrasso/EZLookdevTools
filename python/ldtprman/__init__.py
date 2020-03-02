"""
.. module:: ldtprman
   :synopsis: renderman miscelaneous functions.

.. moduleauthor:: Ezequiel Mastrasso

"""

import os
import sys
import logging
import platform
import subprocess

logger = logging.getLogger(__name__)

# Were are assuming txmake exists in the PATH, and is all ready to go.
PLATFORM = platform.system()
if PLATFORM == 'Windows':
    TXMAKE_EXEC = 'txmake.exe'
else:
    TXMAKE_EXEC = 'txmake'


def convert_to_tx(file_list):
    """
    Convert a list of full path files into tx textures.

    Args:
        file_list (list): list of file paths.

    Raises:
        OSError.

    """
    for file_path in file_list:
        file_basename = os.path.basename(file_path)
        basename = os.path.basename(file_path)
        file_name = os.path.splitext(basename)[0]
        folder = os.path.dirname(file_path)
        tex_file_path = os.path.join(folder, (file_name+'.tex'))
        try:
            # example command line
            # txmake -compression dwaa -mode periodic in.tif out.tex
            logger.info('Converting %s into .tex format' % basename)
            subprocess.call([TXMAKE_EXEC,
                             '-compression',
                             'dwaa',
                             '-mode',
                             'periodic',
                             file_path,
                             tex_file_path])
        except OSError:
            logger.error('txmake was not found in the PATH!')
