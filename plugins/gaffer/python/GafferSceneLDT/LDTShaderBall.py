import IECore

import Gaffer
import GafferArnold
import GafferScene
import imath

# \todo Nice geometry


class LDTShaderBall(GafferScene.SceneNode):
    def __init__(self, name="LDTShaderBall"):

        GafferScene.SceneNode.__init__(self, name)

        # Public plugs

        self["shader"] = GafferScene.ShaderPlug()
        self["resolution"] = Gaffer.IntPlug(
            defaultValue=512, minValue=0
        )
        self["custom_geo"] = Gaffer.StringPlug(
            defaultValue="${LOOKDEVTOOLS}/resources/abc/teapot.abc"
        )
        self["custom_geo_scale"] = Gaffer.FloatPlug(
            defaultValue=1.0
        )

        # Private internal network

        # Custom geo
        self["__teapot"] = GafferScene.SceneReader()
        self["__teapot"]["fileName"].setInput(
            self["custom_geo"]
        )
        self["__teapot"]["transform"]["scale"].setValue(
            imath.V3f(
                0.0500000007, 0.0500000007, 0.0500000007
            )
        )

        self["MeshType1"] = GafferScene.MeshType(
            "MeshType1"
        )
        self["PathFilter7"] = GafferScene.PathFilter(
            "PathFilter7"
        )
        self["MeshType1"]["filter"].setInput(
            self["PathFilter7"]["out"]
        )
        self["MeshType1"]["meshType"].setValue(
            "catmullClark"
        )
        self["PathFilter7"]["paths"].setValue(
            IECore.StringVectorData(["/..."])
        )

        self["MeshType1"]["in"].setInput(
            self["__teapot"]["out"]
        )

        # Root
        self["__root"] = GafferScene.Group()
        self["__root"]["transform"]["scale"]["x"].setInput(
            self["custom_geo_scale"]
        )
        self["__root"]["transform"]["scale"]["y"].setInput(
            self["custom_geo_scale"]
        )
        self["__root"]["transform"]["scale"]["z"].setInput(
            self["custom_geo_scale"]
        )
        self["__root"]["in"][0].setInput(
            self["MeshType1"]["out"]
        )

        self["__camera"] = GafferScene.Camera()
        self["__camera"]["transform"]["translate"].setValue(
            imath.V3f(0, 2.29999995, 9.5)
        )
        self["__camera"]["transform"]["rotate"].setValue(
            imath.V3f(-9, 0, 0)
        )
        self["__camera"]["fieldOfView"].setValue(20.0)

        self["__group"] = GafferScene.Group()
        self["__group"]["in"][0].setInput(
            self["__root"]["out"]
        )
        self["__group"]["in"][1].setInput(
            self["__camera"]["out"]
        )
        # self["__group"]["in"][2].setInput(self["__plane"]["out"])

        self["__subTree"] = GafferScene.SubTree()
        self["__subTree"]["in"].setInput(
            self["__group"]["out"]
        )
        self["__subTree"]["root"].setValue("/group")

        self[
            "__shaderAssignment"
        ] = GafferScene.ShaderAssignment()
        self["__shaderAssignment"]["in"].setInput(
            self["__subTree"]["out"]
        )
        self["__shaderAssignment"]["shader"].setInput(
            self["shader"]
        )

        self["__options"] = GafferScene.StandardOptions()
        self["__options"]["in"].setInput(
            self["__shaderAssignment"]["out"]
        )

        self["__options"]["options"]["renderCamera"][
            "enabled"
        ].setValue(True)
        self["__options"]["options"]["renderCamera"][
            "value"
        ].setValue("/camera")

        self["__options"]["options"]["renderResolution"][
            "enabled"
        ].setValue(True)
        self["__options"]["options"]["renderResolution"][
            "value"
        ][0].setInput(self["resolution"])
        self["__options"]["options"]["renderResolution"][
            "value"
        ][1].setInput(self["resolution"])

        self["__emptyScene"] = GafferScene.ScenePlug()
        self["__enabler"] = Gaffer.Switch()
        self["__enabler"].setup(GafferScene.ScenePlug())
        self["__enabler"]["in"][0].setInput(
            self["__emptyScene"]
        )
        self["__enabler"]["in"][1].setInput(
            self["__options"]["out"]
        )
        self["__enabler"]["enabled"].setInput(
            self["enabled"]
        )
        self["__enabler"]["index"].setValue(1)

        self["out"].setFlags(
            Gaffer.Plug.Flags.Serialisable, False
        )
        self["out"].setInput(self["__enabler"]["out"])

    # Internal plug which the final scene is connected into.
    # Derived classes may insert additional nodes between this
    # plug and its input to modify the scene.
    def _outPlug(self):

        return self["__enabler"]["in"][1]


IECore.registerRunTimeTyped(
    LDTShaderBall, typeName="GafferScene::ShaderBall"
)
