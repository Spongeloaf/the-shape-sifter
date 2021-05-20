import threading
import commonUtils as cu
from commonUtils import ImageBundle
import os
from typing import List
import sqlite3
import fileUtils as fu


def MakeBundleFromForm(form, user_id):
    try:
        partNum = form['partNum']
        puid = form['puid']
        images = cu.ImageStrToList(form['images'])

        return ImageBundle(images, puid, user_id, partNum)
    except:
        return None


class ImageManager:
    """
    The ImageManager will track the files available for sorting and flag files that have been sent to a user for
    classification. When a user loads the classification page (labelling.py), the page will display at least one image
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
        self.folder = settings.unlabelledPartsPath
        self.bundleList = []
        self.__CreateBundleList__()
        self.mainDB = cu.settings.mainDB
        self.labelledDB = cu.settings.labelledPartsDB
        self.__PruneDB__()
        self.__AddImagesToDB__()

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
            self.bundleList.append(ImageBundle([file], PUID, 0, ""))
            return

        for bundle in self.bundleList:
            if bundle.PUID == PUID:
                bundle.images.append(file)
                return

        self.bundleList.append(ImageBundle([file], PUID, 0, ""))

    def __FindBundle__(self, puid):
        """ Gets the pictures of a given PUID from the image list """
        for bundle in self.bundleList:
            if puid == bundle.PUID:
                return bundle.images
        return []

    def __CreateBundleList__(self):
        """ This function creates a list of file bundles in the unknowParts directory. """
        walker = os.walk(self.folder, topdown=False)
        bundle = ImageBundle
        bundle.PUID = ""
        try:
            for root, dirs, files in walker:
                for f in files:
                    # Grab the first file in the directory
                    PUID = self.FileNameToPUID(f)
                    if PUID != "":
                        self.__AddToList__(PUID, f)
        except Exception as e:
            print("Python Error in GetImageBundle(): {}".format(str(e)))

    def __AddImagesToDB__(self):
        """ Loops through the image bundle list and adds bundles to the SQL db if they don't exist."""
        sql = sqlite3.connect(self.mainDB)
        for bundle in self.bundleList:
            # TODO: Fix this! We needto serialize the image list in a sqlite friendly way. Maybe we can make it BLOB?
            query = "INSERT OR IGNORE INTO unlabelledParts(puid, user, images) VALUES ({}, {}, {})".format(bundle.PUID, 0, bundle.images)
            sql.execute(query)
        sql.commit()

    def DoesPUIDHaveBundle(self, puid):
        """ Retruns true if a given PUID has an image bundle on the disk. """
        for bundle in self.bundleList:
            if bundle.PUID == puid:
                return True
        return False

    def __PruneDB__(self):
        """ Removes any part from the live db if its image bundle cannot be located. """
        sql = sqlite3.connect(self.mainDB)
        cursor = sql.cursor()
        cursor.execute("SELECT * from unlabelledParts")
        rows = cursor.fetchall()
        cursor.close()

        # row[0] = puid, row[1] = user, row[2] = images
        for row in rows:
            if not self.DoesPUIDHaveBundle(row[0]):
                sql.execute("DELETE FROM unlabelledParts WHERE puid = {}".format(row[0]))
        sql.commit()

    def GetImageBundle(self, user):
        """
        Gets an image bundle from the database. If the user has a bundle already assigned to them, it will be fewtched.
        Otherwise, the user gets a new bundle from the database.

        DB rows unpack into ImageBundle members: row[0] = puid, row[1] = user, row[2] = images
        """
        # No user should have id 0; It represents parts that have not been assigned to a user
        if user == 0:
            return None

        sql = sqlite3.connect(self.mainDB)
        query = "SELECT * FROM unlabelledParts WHERE user = {} LIMIT 1".format(user)
        cursor = sql.cursor()
        cursor.execute(query)
        if cursor.rowcount < 1:
            # The user should get a new unlabelled part
            query = "SELECT * FROM unlabelledParts WHERE user = 0 LIMIT 1"
            cursor.execute(query)
            if cursor.rowcount < 1:
                # No images left!
                return None
            row = cursor.fetchone()
            return ImageBundle(row[0], row[1], row[2])
        else:
            # The user has a part already assigned to them
            row = cursor.fetchone()
            return ImageBundle(row[0], row[1], row[2])

    def __RemoveBundleFromDB__(self, bundle: ImageBundle):
        sql = sqlite3.connect(self.mainDB)
        cursor = sql.cursor()
        query = "DELETE FROM unlabelledParts WHERE puid = %s'"
        cursor.execute(query, bundle.PUID)

    def __LogBundle__(self):
        # TODO: Log the labelling of parts here!
        pass

    def LabelImageBundle(self, bundle):
        """
        Takes a bundle object and labels it. Labelling involves moving the files from the unlabelled directory to
        the labelled directory and tracking the labelling in the DB.
        """
        fu.MoveFiles(bundle)
        self.__RemoveBundleFromDB__(bundle)
        self.__LogBundle__(bundle)
        pass

imageMgr = ImageManager(cu.settings)
