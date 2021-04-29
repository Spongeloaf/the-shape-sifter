import sys
import subprocess
import random
import datetime
import colorsys

def get_google_drive_path():
    """
    Get Google Drive path on windows machines. The returned string does not have trailing slashes.
    :return: str
    """
    # this code written by /u/Vassilis Papanikolaou from this post:
    # https://stackoverflow.com/a/53430229/10236951

    import sqlite3
    import os

    db_path = (os.getenv('LOCALAPPDATA') + '\\Google\\Drive\\user_default\\sync_config.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * from data where entry_key = 'local_sync_root_path'")
    res = cursor.fetchone()
    path = res[2][4:]
    db.close()

    full_path = path + '\\software_dev\\the_shape_sifter'

    return full_path


# ---------------------------------------------------------------------------------
# MAIN SETUP - Define your main options here
#
# For a single part render, use mode = 1
# For a multipart render, use mode = 2
#
# For a random viewing angle, use angle = "random"
# for a preset one, use "45", "90", "270" "lg", or make your own
#
# For a random color, use "random"
# For a set color, use a color string formatted like this: 0x0066ff (this color is blue)
# ---------------------------------------------------------------------------------
mode = 1
view_angle = "random"
color = "random"
batch_size = 50
ldrawFolder = get_google_drive_path() + "\\ldraw"
partsFolder = ldrawFolder + "\\parts"
mode_1_input_file = "\\3001.dat"
mode_2_input_list = "C:\\Users\\Spongeloaf\\Google Drive\\peter\\python projects\\machine learning\\ldraw_render\\plates.txt"
output_dir = ldrawFolder + "\\out"


# ---------------------------------------------------------------------------------
# PARAM SETUP - Define your Ldraw params here
# This set has been tweaked for neural net generation.
# If you wish to change these, please make a copy and comment these out.
# ---------------------------------------------------------------------------------
general_params = "-Antialias=4 -LineSmoothing=1 -TransDefaultColor=0  -PrintBackground=1 -BackgroundColor3=0x010101 -ProcessLDConfig=1 -MemoryUsage=2"
geometry_params = "-Seams=0 -SeamWidth=0 -BoundingBoxesOnly-0 -Wireframe=0 -RemoveHiddenLines=0 -WireframeFog=0 -WireframeThickness=5 -BFC=0 -ShowHighlightLines=1 -EdgesOnly=0 -ConditionalHighlights=1 -ShowAllType5=0 -ShowType5ControlPoints=0 -PolygonOffset=1 -BlackHighlights=0 -EdgeThickness=1"
effects_params = "-Lighting=1 -UseQualityLighting=1 -SubduedLighting=0 -UseSpecular=1 -OneLight=0 -LightVector=-1,1,1 -OptionalStandardLight=1 -DrawLightDats=1 -NoLightGeom=0 -StereoMode=0 -CutawayMode=0 -SortTransparent=1 -UseStipple=0 -UseFlatShading=0 -PerformSmoothing=1"
primitives_params = "-AllowPrimitiveSubstitution=1 -TextureStuds=1 -HiResPrimitive=1 -UseQualityStuds=1 -CurveQuality=12 -TextureFilterType=9984"
save_params = "-AutoCrop=1 -ModelSize=200 -SaveActualSize=0 -SaveZoomToFit=0 -SaveWidth=1000 -SaveHeight=1000 -IgnorePBuffer=0 -SaveAlpha=1"

# ---------------------------------------------------------------------------------
# PERSPECTIVE SETUP - Dictinonary of perspectives.
# Only used in not random orientation.
# ---------------------------------------------------------------------------------
perspectives = {
    "270" : "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=-0.5,0,-0.866025,-0.496732,0.819152,0.286788,0.709407,0.573576,-0.409576",
    "90" : "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.476843,0,0.878989,0.484195,0.834601,-0.262671,-0.733605,0.550854,0.397974",
    "45" : "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.800476,0,0.599365,0.303928,0.861897,-0.405909,-0.51659,0.507084,0.689928",
    "lg" : "-FOV=0.1 -DefaultZoom=0.85 -DefaultMatrix=0.476843,0,0.878989,0.484195,0.834601,-0.262671,-0.733605,0.550854,0.397974",
    "test": "-FOV=0.1 -DefaultZoom=0.95 -DefaultLatLong=20,20"
}


# a function to create random numbers for use as rotation values.
# These values may be used randomise the output image's rotation
# Rotation constraints: All rotation integers must avoid any direct views of parts flat on the side, top, or bottom.
# To achieve this, we should ensure our integers must be more than 20 degrees off of any multiple of 90.
def random_orientation():
    quadrant = random.randint(0,3) * 90
    rn = random.randint(20, 70)
    return int(rn + quadrant)


# a function to create a random color!
# this may be used to randomize the output brick's color
def random_color():

    colorSeed = random.randint(0, 100)
    h,s,l = 0,0,0

    # Bold colors
    if colorSeed < 50:
        h = random.randint(0, 100)
        s = random.randint(70, 100)
        l = random.randint(25, 75)

    # Darker colors
    elif colorSeed < 75:
        h = random.randint(0, 100)
        s = random.randint(0, 100)
        l = random.randint(0, 60)

    # Pale colors
    else:
        h = random.randint(0, 100)
        s = random.randint(0, 50)
        l = random.randint(0, 100)

    h  = h / 100
    s  = s / 100
    l  = l / 100

    r,g,b = colorsys.hls_to_rgb(h,l,s)
    r = format(int(r * 256), 'X')
    g = format(int(g * 256), 'X')
    b = format(int(b * 256), 'X')
    color = "0x{0}{1}{2}".format(r, g, b)
    return color




def render_part(render_input_file, output_dir, general_params, geometry_params, effects_params, primitives_params, save_params, color, view_angle):
    if color == "random":
        render_color = "-DefaultColor3={0}".format(random_color())
        # print("random color:")
        # print(render_color)
    else:
        render_color = "-DefaultColor3={0}".format(color)
        # print("fixed color:")
        # print(render_color)

    # if true, randomize the view angle using our random orientation function. See the LDview docs for more info
    if view_angle == "random":
        latitude = random_orientation()
        longitude = random_orientation()
        print(latitude, longitude)
        render_view_angle = "-FOV=0.1 -DefaultZoom=0.95 -DefaultLatLong={0},{1}".format(latitude, longitude)

    # If we are not using random orientation, then use one predefined in the perspectives dict.
    else:
        render_view_angle = perspectives[view_angle]

    # get the full input file path from the input_dir + file_name
    fileName = '"{0}{1}"'.format(partsFolder, render_input_file)
    # print('Input file name: ', fileName)

    # get the full output file path from the output_dir + file_name
    fileOutName = '-SaveSnapshot="' + output_dir + render_input_file[:-4] + '_{0}.png"'.format(index)
    # print('Output file name: ', fileOutName)

    #collect all the params
    params = "{0} {1} {2} {3} {4} {5} {6} {7} {8}".format(fileName, fileOutName, general_params, geometry_params, effects_params, primitives_params, save_params, render_color, render_view_angle)

    # # print the command that we plan to execute, for posterity.
    # print('Executing: "C:\\Program Files\\LDView\\LDView64.exe" {0}'.format(params))

    # this command invokes LDview to render the part, after collecting all of our params
    subprocess.Popen('"C:\\Program Files\\LDView\\LDView64.exe" {0}'.format(params), shell=True, stdin=None, close_fds=True)
    # subprocess.Popen("C:\\Program Files\\LDView\\LDView64.exe", shell=True, stdin=None, close_fds=True)
    #subprocess.call('"C:\\Program Files\\LDView\\LDView64.exe" {0}'.format(params), shell=True)
    return



# Begin Main Loop

print('Output dir:{0}'.format(output_dir))
print('Started at {0: %H:%M:%S:%f}'.format(datetime.datetime.now()))

# Generate a batch of images of a single part if mode is 0
if mode == 1:
    for index in range(0, batch_size):
        # simple 1 to 1 conversion of filename for a single part operation
        render_input_file = mode_1_input_file
        #Pass the render_input filename and all the other shit to the function
        render_part(render_input_file, output_dir, general_params, geometry_params, effects_params, primitives_params, save_params, color, view_angle)


    sys.exit()

if mode == 2:
    with open(mode_2_input_list, 'rU') as datafile:
        for line in datafile:
            print(line.strip())
            for index in range(0, batch_size):
                # simple 1 to 1 conversion of filename for a single part operation
                render_input_file = line.strip() + ".dat"
                print(render_input_file)
                #Pass the render_input filename and all the other shit to the function
                render_part(render_input_file, output_dir, general_params, geometry_params, effects_params, primitives_params, save_params, color, view_angle)



print('Finished at {0: %H:%M:%S:%f}'.format(datetime.datetime.now()))
#    for index in range(0, batch_size):