import IECore

import Gaffer
import GafferScene
import GafferArnold
import GafferSceneLDT


class ArnoldLDTShaderBall(GafferSceneLDT.LDTShaderBall):
    def __init__(self, name="ArnoldLDTShaderBall"):

        GafferSceneLDT.LDTShaderBall.__init__(self, name)
        print "ArnoldLDTShaderBall Loaded"
        self["environment"] = Gaffer.StringPlug(
            defaultValue="${GAFFER_ROOT}/resources/hdri/studio.exr"
        )
        self["exposure"] = Gaffer.FloatPlug(defaultValue=0)

        self["__envMap"] = GafferArnold.ArnoldShader()
        self["__envMap"].loadShader("image")
        self["__envMap"]["parameters"]["filename"].setInput(
            self["environment"]
        )

        self["__skyDome"] = GafferArnold.ArnoldLight()
        self["__skyDome"].loadShader("skydome_light")
        self["__skyDome"]["parameters"]["color"].setInput(
            self["__envMap"]["out"]
        )
        self["__skyDome"]["parameters"]["format"].setValue(
            "latlong"
        )
        self["__skyDome"]["parameters"][
            "exposure"
        ].setInput(self["exposure"])
        self["__skyDome"]["parameters"]["camera"].setValue(
            0
        )

        self["__parentLights"] = GafferScene.Parent()
        self["__parentLights"]["in"].setInput(
            self._outPlug().getInput()
        )
        self["__parentLights"]["child"].setInput(
            self["__skyDome"]["out"]
        )
        self["__parentLights"]["parent"].setValue("/")

        self[
            "__arnoldOptions"
        ] = GafferArnold.ArnoldOptions()
        self["__arnoldOptions"]["in"].setInput(
            self["__parentLights"]["out"]
        )
        self["__arnoldOptions"]["options"]["aaSamples"][
            "enabled"
        ].setValue(True)
        self["__arnoldOptions"]["options"]["aaSamples"][
            "value"
        ].setValue(3)

        self.addChild(
            self["__arnoldOptions"]["options"][
                "threads"
            ].createCounterpart(
                "threads", Gaffer.Plug.Direction.In
            )
        )
        self["__arnoldOptions"]["options"][
            "threads"
        ].setInput(self["threads"])

        self._outPlug().setInput(
            self["__arnoldOptions"]["out"]
        )


IECore.registerRunTimeTyped(
    ArnoldLDTShaderBall,
    typeName="GafferArnold::ArnoldLDTShaderBall",
)
