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
        
        self["scene"] = Gaffer.IntPlug("scene")
        Gaffer.Metadata.registerValue( self["scene"], 'nodule:type', '' )
        Gaffer.Metadata.registerValue( self["scene"], 'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget' )
        Gaffer.Metadata.registerValue( self["scene"], 'preset:shaderBall', 0 )
        Gaffer.Metadata.registerValue( self["scene"], 'preset:customGeo', 1 )

        self["custom_geo"] = Gaffer.StringPlug(
            defaultValue="${LOOKDEVTOOLS}/resources/assets/teapot/teapot.abc"
        )

        # Private internal network

        # ShaderBall
        s = Gaffer.ScriptNode()
        __shaderBallReference = s["__shaderBallReference"] = Gaffer.Reference()
        __shaderBallReference.load("/run/media/ezequielm/misc/wrk/dev/EZLookdevTools/plugins/gaffer/boxes/LDTShaderBall.grf")

        self.addChild(__shaderBallReference)

        # Custom geo
        self["__teapot"] = GafferScene.SceneReader()
        self["__teapot"]["fileName"].setInput(
            self["custom_geo"]
        )
        self["__teapot"]["transform"]["scale"].setValue(
            imath.V3f(
                1, 1, 1
            )
        )

        self["__teapotMeshType"] = GafferScene.MeshType("__teapotMeshType")
        self["__teapotPathFilter"] = GafferScene.PathFilter("__teapotPathFilter")
        self["__teapotMeshType"]["filter"].setInput(self["__teapotPathFilter"]["out"])
        self["__teapotMeshType"]["meshType"].setValue("catmullClark")
        self["__teapotPathFilter"]["paths"].setValue(IECore.StringVectorData(["/..."]))

        self["__teapotMeshType"]["in"].setInput(self["__teapot"]["out"])

        self["__teapotSet"] = GafferScene.Set( "SHADERBALL_material" )
        self["__teapotSet"]["name"].setValue( 'SHADERBALL:material' )
        self["__teapotSet"]["filter"].setInput(self["__teapotPathFilter"]["out"])
        self["__teapotSet"]["in"].setInput(self["__teapotMeshType"]["out"])

        # Root
        self["__sceneSwitch"] = Gaffer.Switch()
        self["__sceneSwitch"].setup(GafferScene.ScenePlug( "in"))
        self["__sceneSwitch"]["index"].setInput(self["scene"])
        self["__sceneSwitch"]["in"].addChild( GafferScene.ScenePlug( "in0", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )
        self["__sceneSwitch"]["in"].addChild( GafferScene.ScenePlug( "in1", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

        self["__sceneSwitch"]["in"]["in0"].setInput(self["__shaderBallReference"]["out"])
        self["__sceneSwitch"]["in"]["in1"].setInput(self["__teapotSet"]["out"])

        self["__camera"] = GafferScene.Camera()
        self["__camera"]["transform"]["translate"].setValue(imath.V3f(0, 70, 175))
        self["__camera"]["transform"]["rotate"].setValue(imath.V3f(-16, 0, 0))
        self["__camera"]["fieldOfView"].setValue(20.0)
        self["__group"] = GafferScene.Group()
        self["__group"]["in"][0].setInput(
            self["__sceneSwitch"]["out"]
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

        self["__shaderAssignment"] = GafferScene.ShaderAssignment()
        self["__shaderAssignment"]["in"].setInput(
            self["__subTree"]["out"]
        )
        self["__shaderAssignment"]["shader"].setInput(
            self["shader"]
        )
        self["__shaderAssignmentFilter"] = GafferScene.SetFilter( "SetFilter" )
        self["__shaderAssignmentFilter"]["setExpression"].setValue( 'SHADERBALL:material' )

        self["__shaderAssignment"]["filter"].setInput(self["__shaderAssignmentFilter"]["out"])


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
