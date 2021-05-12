import sys
import subprocess
import random
import datetime
import colorsys
import os
import commonUtils as cu


class __RendererImplementation:
    ldrawFolder: str
    outputFolder: str
    inputFolder: str
    color: str
    view_angle: str
    general_params: str
    geometry_params: str
    effects_params: str
    primitives_params: str
    save_params: str
    ldViewPath: str

    # ---------------------------------------------------------------------------------
    # PERSPECTIVE SETUP - Dictionary of perspectives. Only used in not random orientation.
    # These are hard-coded only because storing them in a conffig file is a pain in the ass
    # that I can't be bothered to deal with right now.
    # ---------------------------------------------------------------------------------
    perspectives = {
        "270": "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=-0.5,0,-0.866025,-0.496732,0.819152,0.286788,0.709407,0.573576,-0.409576",
        "90": "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.476843,0,0.878989,0.484195,0.834601,-0.262671,-0.733605,0.550854,0.397974",
        "45": "-FOV=0.1 -DefaultZoom=0.95 -DefaultMatrix=0.800476,0,0.599365,0.303928,0.861897,-0.405909,-0.51659,0.507084,0.689928",
        "lg": "-FOV=0.1 -DefaultZoom=0.85 -DefaultMatrix=0.476843,0,0.878989,0.484195,0.834601,-0.262671,-0.733605,0.550854,0.397974",
        "test": "-FOV=0.1 -DefaultZoom=0.95 -DefaultLatLong=20,20"
    }

    def __init__(self):
        ini = cu.settings.GetIni()
        self.ldrawFolder = cu.settings.assetPath + ini.get('renderer', 'ldrawFolder')
        self.outputFolder = cu.settings.renderedImageFolder
        self.inputFolder = self.ldrawFolder + ini.get('renderer', 'inputFolder')
        self.color = ini.get('renderer', 'color')
        self.view_angle = ini.get('renderer', 'view_angle')
        self.general_params = ini.get('renderer', 'general_params')
        self.geometry_params = ini.get('renderer', 'geometry_params')
        self.effects_params = ini.get('renderer', 'effects_params')
        self.primitives_params = ini.get('renderer', 'primitives_params')
        self.save_params = ini.get('renderer', 'save_params')
        self.ldViewPath = ini.get('renderer', 'ldViewPath')

    @staticmethod
    def __random_color__():
        """ Generates random colors for bricks """
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


    def __YieldFiles__(self):
        """ Gets all part images in the input folder. Ignores subfolders which contain unwanted ldraw artifacts. """
        for root, dirs, files in os.walk(self.inputFolder, topdown=True):
            # Do not enter sub folders.
            dirs[:] = []
            for file in files:
                yield file

    def RenderPart(self, partNum):
        """ Renders a single part. This is a blocking render that waits until the process is finished. """
        inFile = partNum + ".dat"
        inPath = os.path.join(self.inputFolder, inFile)
        try:
            if os.path.isfile(inPath):
                self.__InvokeRenderer__(inFile)
                return True
        except:
            return False

    def __InvokeRenderer__(self, inFile: str):
        """ Renders a single part """
        if self.color == "random":
            render_color = "-DefaultColor3={0}".format(self.__random_color__())
        else:
            render_color = "-DefaultColor3={0}".format(self.color)

        # if true, randomize the view angle using our random orientation function. See the LDview docs for more info
        if self.view_angle == "random":
            latitude = random_orientation()
            longitude = random_orientation()
            print(latitude, longitude)
            render_view_angle = "-FOV=0.1 -DefaultZoom=0.95 -DefaultLatLong={0},{1}".format(latitude, longitude)

        # If we are not using random orientation, then use one predefined in the perspectives dict.
        else:
            render_view_angle = self.perspectives[self.view_angle]

        inFilePath = os.path.join(self.inputFolder, inFile)
        inFilePath = '"{}"'.format(inFilePath)
        outFile = os.path.splitext(os.path.basename(inFile))
        outFilePath = '-SaveSnapshot="' + os.path.join(self.outputFolder, outFile[0]) + '.png"'
        params = '{} {} {} {} {} {} {} {} {}'.format(inFilePath, outFilePath, self.general_params, self.geometry_params, self.effects_params, self.primitives_params, self.save_params, render_color, render_view_angle)

        # Invoke LDVieiw
        command = '"{}" {}'.format(self.ldViewPath, params)
        subprocess.call(command, shell=True)
        return

renderer = __RendererImplementation()
