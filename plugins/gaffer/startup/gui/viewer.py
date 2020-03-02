import imath
import Gaffer
import GafferImage
import GafferScene
import GafferSceneUI
import functools

def __createLDTPatternShader2k() :
    pattern = GafferScene.SceneProcessor( "pattern" )

    pattern["shaderAssignment"] = GafferScene.ShaderAssignment( "TextureShaderAssignment" )
    pattern["texture"] = GafferScene.OpenGLShader( "Texture" )
    pattern["texture"].loadShader( "Texture" )
    pattern["texture"]["parameters"]["tint"].setValue( imath.Color4f( 1, 1, 1, 1 ) )
    pattern["texture"]["parameters"]["mult"].setValue( 1.0 )
    pattern["image"] = GafferImage.ImageReader( "ImageReader" )
    pattern["image"]["fileName"].setValue( '${LOOKDEVTOOLS}/resources/patterns/2048x2048_Texel_Density_Texture_1.png' )
    pattern["image"]["colorSpace"].setValue( 'ACES - ACEScg' )

    pattern["texture"]["parameters"]["texture"].setInput(pattern["image"]["out"])
    pattern["shaderAssignment"]["shader"].setInput(pattern["texture"]["out"])
    pattern["shaderAssignment"]["in"].setInput(pattern["in"])
    pattern["out"].setInput(pattern["shaderAssignment"]["out"])

    return pattern

GafferSceneUI.SceneView.registerShadingMode( "LDTPattern2k", functools.partial( __createLDTPatternShader2k ) )

def __createLDTPatternShader4k() :
    pattern = GafferScene.SceneProcessor( "pattern" )

    pattern["shaderAssignment"] = GafferScene.ShaderAssignment( "TextureShaderAssignment" )
    pattern["texture"] = GafferScene.OpenGLShader( "Texture" )
    pattern["texture"].loadShader( "Texture" )
    pattern["texture"]["parameters"]["tint"].setValue( imath.Color4f( 1, 1, 1, 1 ) )
    pattern["texture"]["parameters"]["mult"].setValue( 1.0 )
    pattern["image"] = GafferImage.ImageReader( "ImageReader" )
    pattern["image"]["fileName"].setValue( '${LOOKDEVTOOLS}/resources/patterns/4096x4096_Texel_Density_Texture_1.png' )
    pattern["image"]["colorSpace"].setValue( 'ACES - ACEScg' )

    pattern["texture"]["parameters"]["texture"].setInput(pattern["image"]["out"])
    pattern["shaderAssignment"]["shader"].setInput(pattern["texture"]["out"])
    pattern["shaderAssignment"]["in"].setInput(pattern["in"])
    pattern["out"].setInput(pattern["shaderAssignment"]["out"])

    return pattern

GafferSceneUI.SceneView.registerShadingMode( "LDTPattern4k", functools.partial( __createLDTPatternShader4k ) )
