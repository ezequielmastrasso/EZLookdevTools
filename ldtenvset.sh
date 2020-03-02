#! /bin/bash
#
# Environment Settings
#
# Look Dev Tools

# LOOKDEVTOOLS
# Replace this path with your own
export LOOKDEVTOOLS="/nas/emc_1/wrk/dev/EZLookdevTools"

## PYTHON
export PYTHONPATH="${PYTHONPATH}:$LOOKDEVTOOLS/python"

# NUKE
export NUKE_PATH=$NUKE_PATH:$LOOKDEVTOOLS/plugins/nuke/plugins

# KATANA
export LOOKDEVTOOLS_KATANA_ROOT=$LOOKDEVTOOLS/plugins/katana
export LOOKDEVTOOLS_KATANA_TOOLS=$LOOKDEVTOOLS/plugins/katana/katana_tools
export LOOKDEVTOOLS_KATANA_SHELVES=$LOOKDEVTOOLS/plugins/katana/katana_shelves
export KATANA_RESOURCES=$KATANA_RESOURCES:$LOOKDEVTOOLS_KATANA_TOOLS:$LOOKDEVTOOLS_KATANA_SHELVES:$KAT_SHELVE

# RENDERMAN
# MAKE SURE YOU HAVE RMANTREE and $RMANTREE/bin IN YOUR $PATH