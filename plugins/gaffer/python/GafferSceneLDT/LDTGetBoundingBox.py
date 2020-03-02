import IECore
import math
import imath
import Gaffer
import GafferScene

"""
class LDTGetBoundingBox(GafferScene.SceneNode):

    def __init__(self, name="LDTGetBoundingBox"):
        super(LDTGetBoundingBox, self).__init__(name)
        self["in"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.In)
        self["myValue"] = Gaffer.StringPlug()
        self["myOtherValue"] = Gaffer.StringPlug()
        self["out"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.Out)
        self["out"].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self["out"].setInput(self["in"])
        self.__plugInputChanged = self.plugInputChangedSignal().connect (self.do_that_thing )
        self.__plugValueChanged = self.plugSetSignal().connect ( self.do_that_thing )

    def do_that_thing(self,plug):
        if plug.getName() in ["in","myValue", "myOtherValue"]:
            # set othe plug values here
            print ("Doing it, setting plugs and stuff, %s" %plug)

"""
class LDTGetBoundingBox(GafferScene.SceneNode):

    def __init__(self, name="LDTGetBoundingBox"):
        super(LDTGetBoundingBox, self).__init__(name)
        # create a Gaffer scene reader
        # connect the reader's output to the output
        self.setName("BoundBoxReader")
        self["in"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.In)

        # Make path read only for now
        # TODO: check if path exists
        # TODO: get bounding box in world space
        self["path"] = Gaffer.StringPlug()
        self["path"].setValue("/")
        self["bound"] = Gaffer.Box3fPlug()
        Gaffer.Metadata.registerValue( self["bound"], 'readOnly', True )
        self["boundDiagonalLength"] = Gaffer.FloatPlug()
        Gaffer.Metadata.registerValue( self["boundDiagonalLength"], 'readOnly', True )
        self["boundSize"] = Gaffer.V3fPlug()
        Gaffer.Metadata.registerValue( self["boundSize"], 'readOnly', True )

        self["boundCenter"] = Gaffer.V3fPlug()
        Gaffer.Metadata.registerValue( self["boundCenter"], 'readOnly', True )

        self["out"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.Out)
        self["out"].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self["out"].setInput(self["in"])
        self.__plugInputChanged = self.plugInputChangedSignal().connect (self.get_bound )
        self.__plugValueChanged = self.plugSetSignal().connect(self.get_bound)

    def get_bound( self , plug):
        if plug.getName() in ["in","path"]:
            with Gaffer.BlockedConnection ( self.__plugValueChanged), Gaffer.BlockedConnection ( self.__plugInputChanged):
                bound = self["in"].bound(self["path"].getValue())
                if bound.isEmpty():
                    self["bound"].setValue(imath.Box3f(imath.V3f(0,0,0),imath.V3f(0,0,0)))
                    self["boundDiagonalLength"].setValue(0.0)
                    self["boundSize"].setValue(imath.V3f(0,0,0))
                    self["boundCenter"].setValue(imath.V3f(0,0,0))
                    return
                a=bound.min()
                b=bound.max()
                boundDiagonalLength = math.sqrt(pow((a[0]-b[0]),2) + pow((a[1]-b[1]),2) + pow((a[2]-b[2]),2))
                self["bound"].setValue(bound)
                self["boundDiagonalLength"].setValue(boundDiagonalLength)
                self["boundSize"].setValue(bound.size())
                self["boundCenter"].setValue(bound.center())





IECore.registerRunTimeTyped(
    LDTGetBoundingBox, typeName="GafferScene::LDTGetBoundingBox"
)
