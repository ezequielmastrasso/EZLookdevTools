import IECore
import Gaffer
import GafferArnold
import GafferScene
import imath
import ldtgaffer

class LDTAtttributeRead(GafferScene.SceneNode):
    def __init__(self, name="LDTAtttributeRead"):
        super(LDTAtttributeRead, self).__init__(name)
        self.setName("LDTAtttributeRead")
        self["in"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.In)

        self["path"] = Gaffer.StringPlug()
        self["path"].setValue("/")
        self["attribute"] = Gaffer.StringPlug()
        self["value"] = Gaffer.StringPlug()
        Gaffer.Metadata.registerValue( self["value"], 'readOnly', True )

        self["out"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.Out)
        self["out"].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self["out"].setInput(self["in"])

        self.__plugInputChanged = self.plugInputChangedSignal().connect (self.get_attributes )
        self.__plugValueChanged = self.plugSetSignal().connect(self.get_attributes)

    def get_attributes( self , plug):
        if plug.getName() in ["in","attribute"]:
            attribute = self["attribute"].getValue()
            path = self["path"].getValue()
            try:
                value = self["in"].attributes(path)[attribute]
                print ("LDTAttributeReader: %s, %s, %s" %(path,attribute,value))
                self["value"].setValue(str(value))
            except:
                print ("LDTAttributeReader: %s, %s, %s" %(path,attribute,"None"))
                self["value"].setValue("")
IECore.registerRunTimeTyped(
    LDTAtttributeRead, typeName="GafferScene::LDTAtttributeRead"
)
