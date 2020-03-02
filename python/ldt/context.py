"""
.. module:: context
   :synopsis: DCC related context.

.. moduleauthor:: Ezequiel Mastrasso

"""

import logging
logger = logging.getLogger(__name__)


def dcc():
    """Return the DCC name. Maya, Katana, Gaffer, Nuke, Mari."""
    logger.info('Get DCC context.')
    try:
        import pymel.core
        logger.info('Maya found.')
        return "Maya"
    except:
        pass
    try:
        import Katana
        logger.info('Katana found.')
        return "Katana"
    except:
        pass
    try:
        import GafferScene
        logger.info('Gaffer found.')
        return "Gaffer"
    except:
        pass
    try:
        import mari
        logger.info('Gaffer found.')
        return "Mari"
    except:
        pass
