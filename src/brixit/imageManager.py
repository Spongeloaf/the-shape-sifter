import threading
import commonUtils as cu
import os
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

    def __init__(self, images, PUID, user):
        self.images = images
        self.user = user
        self.PUID = PUID


class ImageManager:
    """
    The ImageManager will track the files available for sorting and flag files that have been sent to a user for
    classification. When a user loads the classification page (sorting.py), the page will display at least one image
    of an unknow part. However, some files come in bundles; multiple images taken by the sorting machine of the same
    part. These bundles follow the naming convention of PUID_XX.png. Files which are not bundled follow the convention
    of PUID.png, note the absent '_' delimiter. Two files with the same PUID are not bundled if they have the same
    number following the '_' delimiter or if one of the files is does not have a delimeter. The index number, XX may be
    a positive integer of any size.

    Say we have the following files:
        wt3bec9oxu40_00.png
        wt3bec9oxu40_420.png
        wt3bec9oxu40_69.png
        c93bn69cgw0s_01.png
        wt3bec9oxu40.png

    In this case, the first three files are considered bundled. The remaining files will not be considered
    bundled with respect to any other file in the list.
    """
    def __init__(self, settings: cu.Settings):
        self.lock = threading.Lock()
        self.folder = settings.unknownPartsPath
        self.bundleList = []
        self.CreateBundleList()

    @staticmethod
    def FileNameToPUID(file: str):
        """
        Takes a filename and extracts the PUID component of the name.
        Input:
            wt3bec9oxu40_69.png
            c93bn69cgw0s_01.png
            wt3bec9oxu40.png

        Output:
            wt3bec9oxu40
            c93bn69cgw0s
            wt3bec9oxu40
        """
        if file == "":
            return file

        strs = file.split('.')
        if len(strs) != 2:
            return ""

        # Only png images are officially supported.
        if strs[1] != "png":
            return ""

        # 'puid_xx.png' > 'puid', 'xx'
        strs = strs[0].split('_')
        return strs[0]

    def __AddToList__(self, PUID: str, file: str):
        """ Adds a file to a matching bundle if it exists.  """
        if len(self.bundleList) == 0:
            self.bundleList.append(ImageBundle([file], PUID, 0))
            return

        for bundle in self.bundleList:
            if bundle.PUID == PUID:
                bundle.images.append(file)
                return

        self.bundleList.append(ImageBundle([file], PUID, 0))

    def CreateBundleList(self):
        """
        This function creates a list of file bundles in the unknowParts directory.
        """
        walker = os.walk(self.folder, topdown=False)
        bundle = ImageBundle
        bundle.PUID = ""
        try:
            for root, dirs, files in walker:
                for f in files:
                    # Grab the first file in the directory
                    PUID = self.FileNameToPUID(f)
                    self.__AddToList__(PUID, f)
        except Exception as e:
            print("Python Error in GetImageBundle(): {}".format(str(e)))

imageMgr = ImageManager(cu.settings)
