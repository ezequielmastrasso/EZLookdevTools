# Viewer Settings > Optimize viewer during playback: on
nuke.knobDefault("Viewer.freezeGuiWhenPlayBack", "1")

# Write > Default for EXR files: 16bit Half, No Compression
nuke.knobDefault("Write.exr.compression", "0")

# Exposure Tool > Use stops instead of densities
# nuke.knobDefault("EXPTool.mode", "0")

# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")

# Custom Resolutions
nuke.addFormat("1920 810 HD-2.37")
nuke.addFormat("960 405 HD-2.37 half")
nuke.addFormat("640 270 HD-2.37 third")
nuke.addFormat("1920 817 HD-2.35")
nuke.addFormat("960 408 HD-2.35 half")
nuke.addFormat("640 272 HD-2.35 third")

# Project Settings > Default format: HD 1920x1080
nuke.knobDefault("Root.format", "HD")
