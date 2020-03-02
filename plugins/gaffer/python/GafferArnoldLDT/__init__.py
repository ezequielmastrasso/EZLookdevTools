from ArnoldLDTShaderBall import ArnoldLDTShaderBall
__import__("GafferScene")

try:

    # Make sure we import IECoreArnold and _GafferArnold
    # _without_ RTLD_GLOBAL. This prevents clashes between the
    # LLVM symbols in libai.so and the Mesa OpenGL driver.
    # Ideally we wouldn't use RTLD_GLOBAL anywhere - see
    # https://github.com/ImageEngine/cortex/pull/810.

    import sys
    import ctypes
    originalDLOpenFlags = sys.getdlopenflags()
    sys.setdlopenflags(originalDLOpenFlags & ~ctypes.RTLD_GLOBAL)

    __import__("IECoreArnold")
    from GafferArnold import *

finally:

    sys.setdlopenflags(originalDLOpenFlags)
    del sys, ctypes, originalDLOpenFlags


__import__("IECore").loadConfig(
    "GAFFER_STARTUP_PATHS", subdirectory="GafferArnold")
