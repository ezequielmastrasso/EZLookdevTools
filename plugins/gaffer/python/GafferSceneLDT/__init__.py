from LDTAtttributeRead import LDTAtttributeRead
from LDTShaderBall import LDTShaderBall
from LDTGetBoundingBox import LDTGetBoundingBox
from GafferScene import *
__import__("IECoreScene")
__import__("Gaffer")
__import__("GafferDispatch")
__import__("GafferImage")

__import__("IECore").loadConfig(
    "GAFFER_STARTUP_PATHS", subdirectory="GafferScene")
