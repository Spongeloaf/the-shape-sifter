import os
import sys
import subprocess
from openpyxl import load_workbook

GENERAL_PARAMS="-Antialias=4 -LineSmoothing=1 -TransDefaultColor=0 -DefaultColor3=0xFFFFFF -BackgroundColor3=0xFFFFFF -ProcessLDConfig=1 -MemoryUsage=2"
GEOMETRY_PARAMS="-Seams=1 -SeamWidth=50 -BoundingBoxesOnly-0 -Wireframe=0 -RemoveHiddenLines=0 -WireframeFog=0 -WireframeThickness=5 -BFC=0 -ShowHighlightLines=1 -EdgesOnly=0 -ConditionalHighlights=1 -ShowAllType5=0 -ShowType5ControlPoints=0 -PolygonOffset=1 -BlackHighlights=1 -EdgeThickness=5"
EFFECTS_PARAMS="-Lighting=1 -UseQualityLighting=1 -SubduedLighting=0 -UseSpecular=1 -OneLight=0 -LightVector=-1,1,1 -OptionalStandardLight=1 -DrawLightDats=1 -NoLightGeom=0 -StereoMode=0 -CutawayMode=0 -SortTransparent=1 -UseStipple=0 -UseFlatShading=0 -PerformSmoothing=1"
PRIMITIVES_PARAMS="-AllowPrimitiveSubstitution=1 -TextureStuds=0 -HiResPrimitive=1 -UseQualityStuds=1 -CurveQuality=12 -TextureFilterType=9984"
SAVE_PARAMS="-AutoCrop=1 -ModelSize=200 -SaveActualSize=0 -SaveZoomToFit=0 -SaveWidth=2000 -SaveHeight=2000 -IgnorePBuffer=0 -SaveAlpha=1"
PARAMS="{0} {1} {2} {3} {4}".format(GENERAL_PARAMS, GEOMETRY_PARAMS, EFFECTS_PARAMS, PRIMITIVES_PARAMS, SAVE_PARAMS,)
PERSPECTIVE270="-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=-0.5,0,-0.866025,-0.496732,0.819152,0.286788,0.709407,0.573576,-0.409576"
PERSPECTIVE90="-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.476843,0,0.878989,0.484195,0.834601,-0.262671,-0.733605,0.550854,0.397974"
PERSPECTIVE45="-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.800476,0,0.599365,0.303928,0.861897,-0.405909,-0.51659,0.507084,0.689928"
PERSPECTIVELG="-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.800476,0,0.599365,0.303928,0.861897,-0.405909,-0.51659,0.507084,0.689928"


FILES="c:\labels\\"
fOutputDir="c:\labels\output_hi\\"

inputFile="3713.dat"

fName='"{0}\{1}"'.format(FILES, inputFile)
print('Input file name: ', fName)

fOutName=fOutputDir+inputFile[:-4]+'_angle.png'
print('Output file name: ', fOutName)


print('Executing: "C:\Program Files\LDView\\LDView64.exe" {0} -SaveSnapshot={3} {1} {2}'.format(fName, PARAMS,PERSPECTIVE45, fOutName))
subprocess.call('"C:\Program Files\LDView\\LDView64.exe" {0} -SaveSnapshot={3} {1} {2}'.format(fName, PARAMS,PERSPECTIVE45, fOutName), shell=True)
