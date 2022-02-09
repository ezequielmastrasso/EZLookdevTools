import IECore
import Gaffer
import GafferArnold
import GafferScene
import imath
import ldtgaffer


class LDTSurfacingSets(GafferScene.SceneNode):
    def __init__(self, name="LDTSurfacingSets"):
        super(LDTSurfacingSets, self).__init__(name)
        self.setName("LDTSurfacingSets")
        self["in"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.In)
        self["path"] = Gaffer.StringPlug( "path", defaultValue = '/')
        self["prefix"] = Gaffer.StringPlug( "prefix", defaultValue = 'surf:')
        self["attribute"] = Gaffer.StringPlug( "attribute", defaultValue = 'surfacing_object')
        self["enabled"] = Gaffer.BoolPlug( "enabled", defaultValue = True)
        self["out"] = GafferScene.ScenePlug(direction = Gaffer.Plug.Direction.Out)
        self["out"].setFlags(Gaffer.Plug.Flags.Serialisable, False)
        self["out"].setInput(self["in"])

        self.__plugInputChanged = self.plugInputChangedSignal().connect(self.buildSets)
        self.__plugValueChanged = self.plugSetSignal().connect(self.buildSets)

    def buildSets(self, plug):
        if plug.getName() in ("in", "prefix", "attribute", "path"):
            nodeIn = self['in']
            nodeOut = self['out']
            prefix = self["prefix"].getValue()
            hio = ldtgaffer.AttributesSearch(
                nodeIn, self["path"].getValue(), self["attribute"].getValue())
            setNodes = {}
            numAttrs = len(hio.attributes.keys())
            for idx, attr in enumerate(list(hio.attributes.keys())):
                setNodes[idx] = GafferScene.Set(attr)
                setNodes[idx]["name"].setValue(prefix + attr)
                self.addChild(setNodes[idx])
                filterNode = GafferScene.PathFilter(attr)
                self.addChild(filterNode)
                setNodes[idx]["filter"].setInput(filterNode["out"])
                filterNode["paths"].setValue(IECore.StringVectorData(hio.attributes[attr]))
                if idx == 0:
                    print("Setting up first set {}".format(prefix + attr))
                    setNodes[idx]["in"].setInput(nodeIn)
                elif idx == numAttrs-1:
                    print("Finalising last set {}".format(prefix + attr))
                    setNodes[idx]["in"].setInput(setNodes[idx-1]["out"])
                    nodeOut.setInput(setNodes[idx]["out"])
                else:
                    print("Connecting {} to {}".format(setNodes[idx-1]["name"].getValue(),
                                                       setNodes[idx]["name"].getValue()))
                    setNodes[idx]["in"].setInput(setNodes[idx-1]["out"])


IECore.registerRunTimeTyped(
    LDTSurfacingSets, typeName="GafferScene::LDTSurfacingSets"
)



