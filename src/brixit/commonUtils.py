import os
import configparser
import sys
from dataclasses import dataclass
from typing import List

class ImageBundle:
    """
    Properties:
        images - A list of image file names
        user   - The user assigned to classify a given bundle
        PUID   - The PUID of the bundle. The PUID is taken from the filename.
                 For a file "c93bn69cgw0s_01.png", the PUID is "c93bn69cgw0s"
    """
    images: List[str]
    user: int
    PUID: str
    partNum: str

    def __init__(self, images, PUID, user, partNum):
        self.images = images
        self.user = user
        self.PUID = PUID
        self.partNum = partNum


@dataclass
class Part:
    partNum: str
    partName: str
    categoryNum: str
    categoryName: str
    stockImage: str
    realImageListStr: str

    # def __int__(self, categoryNum="", categoryName="", partNum="",
    #             partName="", stockImage="", realImages=""):
    #     self.partNum = partNum
    #     self.partName = partName
    #     self.categoryNum = categoryNum
    #     self.categoryName = categoryName
    #     self.stockImage = stockImage
    #     self.realImageListStr = realImages
    #
    # def __init__(self):
    #     self.partNum = ""
    #     self.partName = ""
    #     self.categoryNum = ""
    #     self.categoryName = ""
    #     self.stockImage = ""
    #     self.realImageListStr = ""


def GetGoogleDrivePath():
    """
    Get Google Drive path on windows machines. The returned string does not have trailing slashes.
    :return: str
    """
    # this code written by /u/Vassilis Papanikolaou from this post:
    # https://stackoverflow.com/a/53430229/10236951

    import sqlite3

    db_path = (os.getenv('LOCALAPPDATA') + '\\Google\\Drive\\user_default\\sync_config.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * from data where entry_key = 'local_sync_root_path'")
    res = cursor.fetchone()
    path = res[2][4:]
    db.close()

    full_path = path + '\\software_dev\\the_shape_sifter'

    return full_path


def AreFilesInABundle(f1, f2):
    """
    Some files may be bundled. These bundles follow the naming convention of PUID_XX.png. Files which are not bundled
    follow the convention of PUID.png, note the absent '_' delimiter. Two files with the same PUID are not bundled if
    they have the same number following the '_' delimiter or if one of the files is does not have a delimeter. The index
    number, XX may be a valid integer of any length.

    Say we have the following files:
        wt3bec9oxu40_00.png
        wt3bec9oxu40_420.png
        wt3bec9oxu40_69.png
        c93bn69cgw0s_01.png
        wt3bec9oxu40.png

    In this case, the first three files are considered bundled. The remaining files will not be considered
    bundled with respect to any other file in the list.
    """

    if f1 == f2:
        return False

    split1 = f1.split('.')
    split2 = f2.split('.')

    if (len(split1) != 2) or (len(split2) != 2):
        return False

    fName1 = split1[0]
    fName2 = split2[0]
    ext1 = split1[1]
    ext2 = split2[1]

    if (ext1 != "png") and (ext2 != "png"):
        return False

    haystack1 = fName1.split('_')
    haystack2 = fName2.split('_')

    # Length will be 2 as long as the filename has only one '_' somewhere inside it.
    if (len(haystack1) != 2) or (len(haystack2) != 2):
        return False

    # Ensure both indexes are integers
    try:
        i1 = int(haystack1[1])
        i2 = int(haystack2[1])
    except:
        return False

    if haystack1[0] == haystack2[0]:
        # If we've made it this far, then both files are from the same bundle and have different indexes.
        return True

    return False


def GetPUID(fName):
    """
    Gets a PUID from a file name.
    """
    haystack1 = fName.split('.')
    haystack2 = haystack1.pop(0).split('_')
    return haystack2.pop(0)


def ImageStrToList(images: str):
    """ Takes a serialized string of image file names from a form and converts it to a python list of strings"""
    images = images.replace("[", '')
    images = images.replace("]", '')
    images = images.replace("\\", '')
    images = images.replace("'", '')
    result = images.split(',')
    result = [i.strip() for i in result]
    return result


class Settings:
    assetPath: str
    unlabelledPartsPath: str
    labelledPartsPath: str
    instancePath: str
    mainDB: str
    labelledPartsDB: str
    labelledPartsTxt: str
    partList: str
    numberOfResults: int

    def __init__(self):
        # Don't check the ini file. I want the program to crash immediately if it cannot be read.
        ini = self.GetIni()

        self.assetPath = GetGoogleDrivePath()
        self.unlabelledPartsPath = self.assetPath + ini.get('brixit', 'unlabelledPartsPath')
        self.labelledPartsPath = self.assetPath + ini.get('brixit', 'labelledPartsPath')
        self.mainDB = self.assetPath + ini.get('brixit', 'mainDB')
        self.labelledPartsDB = self.assetPath + ini.get('brixit', 'labelledPartsDB')
        self.labelledPartsTxt = self.assetPath + ini.get('brixit', 'labelledPartsTxt')
        self.partList = self.assetPath + ini.get('brixit', 'partList')
        self.numberOfResults = ini.getint('brixit', 'numberOfResults')
        self.renderedImageFolder = self.assetPath + ini.get('brixit', 'renderedImageFolder')
        self.defaultPartImage = ini.get('brixit', 'defaultPartImage')
        self.conveyorBeltImgFolder = self.assetPath + ini.get('brixit', 'conveyorBeltImgFolder')
        self.skippedImageFolder = self.assetPath + ini.get('brixit', 'skippedImageFolder')
        self.bountyLevel1 = 1
        self.bountyLevel2 = 10
        self.bountyLevel3 = 25

    @staticmethod
    def __GetSettingsFile():
        """ Searches the assset path for a settings file """
        fName = GetGoogleDrivePath() + "\\settings.ini"
        if os.path.isfile(fName):
            return fName

        return None

    def GetIni(self):
        file = self.__GetSettingsFile()
        if file:
            config = configparser.ConfigParser()
            config.read(file)
            return config
        return None


class ImageWalker:
    def __init__(self, settings: Settings):
        self.folder = settings.unlabelledPartsPath
        self.images = self.__GetImageBundle()

    def GetCurrentImageBundle(self):
        return self.images

    def NewImageBundle(self):
        self.images = self.__GetImageBundle()

    def __GetImageBundle(self):
        """ Gets the first file from a directory and tries to find any files from the same bundle """
        try:
            walker = os.walk(self.folder, topdown=False)
            for root, dirs, files in walker:
                # Grab the first file in the directory
                selectedFile = files.pop(0)

                fileStr = selectedFile.split('.')
                if len(fileStr) != 2:
                    continue

                if fileStr[1] != "png":
                    continue

                imageBundle = [selectedFile]
                # Images may be standalone or part of a bundle.
                # Bundled images are in the same folder, add them.
                for f in files:
                    if AreFilesInABundle(selectedFile, f):
                        imageBundle.append(f)
                return imageBundle

        except:
            print("Python Error in GetImageBundle()")
            return None, None


settings = Settings()
imageWalker = ImageWalker(settings)
