import IECore
import Gaffer
import GafferSceneUI
import GafferUI
import os

from GafferArnoldLDT import ArnoldLDTShaderBall
from GafferSceneLDT import LDTShaderBall
from GafferSceneLDT import LDTAtttributeRead
from GafferSceneLDT import LDTGetBoundingBox
from GafferSceneLDT import LDTSurfacingSets

nodeMenu = GafferUI.NodeMenu.acquire(application)
nodeMenu.append(
    path="/LDT/ArnoldLDTShaderBall",
    nodeCreator=ArnoldLDTShaderBall,
    searchText="ArnoldLDTShaderBall",
)
nodeMenu.append(
    path="/LDT/LDTAtttributeRead",
    nodeCreator=LDTAtttributeRead,
    searchText="LDTAtttributeRead",
)

nodeMenu.append(
    path="/LDT/LDTGetBoundingBox",
    nodeCreator=LDTGetBoundingBox,
    searchText="LDTGetBoundingBox",
)

nodeMenu.append(
    path="/LDT/LDTSurfacingSets",
    nodeCreator=LDTSurfacingSets.LDTSurfacingSets,
    searchText="LDTSurfacingSets",
)


print "LDT: nodes added to menu"


with IECore.IgnoredExceptions(ImportError):

    import GafferArnold

    GafferSceneUI.ShaderView.registerRenderer(
        "ai", GafferArnold.InteractiveArnoldRender
    )

    def __arnoldLDTShaderBall():

        result = GafferArnoldLDT.ArnoldLDTShaderBall()

        # Reserve some cores for the rest of the UI
        result["threads"]["enabled"].setValue(True)
        result["threads"]["value"].setValue(-3)

        return result

    GafferSceneUI.ShaderView.registerScene(
        "ai", "Default", ArnoldLDTShaderBall
    )
    print "ArnoldLDTShaderBall: GafferSceneUI.ShaderView.registerScene"
