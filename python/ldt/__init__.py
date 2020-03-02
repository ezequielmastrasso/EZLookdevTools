"""
.. module:: ldt
   :synopsis: Look Dev Tools.

.. moduleauthor:: Ezequiel Mastrasso

"""
import sys
import os
import logging
logger = logging.getLogger(__name__)

LOOKDEVTOOLS_PYTHON = os.path.join(
    os.environ['LOOKDEVTOOLS'], 'python', 'external')

if LOOKDEVTOOLS_PYTHON not in sys.path:
    logger.info('Appending external packages folder to sys.path: %s'
                % LOOKDEVTOOLS_PYTHON)
    sys.path.append(LOOKDEVTOOLS_PYTHON)
else:
    logger.info('External packages folder already exists in sys.path, skipping: %s'
                % LOOKDEVTOOLS_PYTHON)
try:
    from Qt.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
    from Qt import QtGui, QtWidgets, QtCore
    import ldtui
    from yapsy.PluginManager import PluginManager
except:
    raise RuntimeError('Failed to load external modules')


def add_ldt_menus():
    """Add Look dev Tools menus to dccs."""
    from ldt import context
    dcc = context.dcc()
    if dcc == 'Maya':
        import pymel.core as pm
        if pm.menu('LookDevTools', l=u'LookDevTools', ex=True):
            logger.info('menu already exists.')
        else:
            pm.menu('LookDevTools', l=u'LookDevTools', to=True)
            pm.menuItem(l=u'Open', c='import ldt;reload(ldt)')
            pm.setParent("..")


def load_plugins():
    """Loads plugins from the puglins folder"""

    plugins = PluginManager()
    plugins_folder = os.path.join(
        os.environ['LOOKDEVTOOLS'], 'python', 'ldtplugins')
    print plugins_folder
    plugins.setPluginPlaces([plugins_folder])
    plugins.collectPlugins()
    plugins.locatePlugins()
    logger.info('Plugin candidates %s' %
                plugins.getPluginCandidates())
    for pluginInfo in plugins.getAllPlugins():
        plugins.activatePluginByName(pluginInfo.name)
        logger.info('Plugin activated %s' %
                    plugins.activatePluginByName(pluginInfo.name))
    return plugins


add_ldt_menus()

plugins = load_plugins()

main_window = QApplication.instance()
if main_window:
    app = main_window
else:
    app = QApplication(sys.argv)
ldt_window = ldtui.LDTWindow(plugins)
ldt_window.show()
