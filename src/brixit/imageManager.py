import threading
import commonUtils as cu
from commonUtils import ImageBundle
import os
from typing import List
import sqlite3
import fileUtils as fu


def MakeBundleFromForm(form, user_id):
    if ('partNum' in form) and ('puid' in form) and ('images' in form):
        return ImageBundle(cu.ImageStrToList(form['images']), form['puid'], user_id, form['partNum'])
    return None


class ImageManager:
    """
    The ImageManager will track the files available for labelling and flag files that have been sent to a user for
    classification. When a user loads the classification page (labelling.py), the page will display at least one image
    of an unknow part. However, some files come in bundles; multiple images taken by the labelling machine of the same
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

    def __FindBundleFromPUID__(self, puid):
        """ Gets the pictures of a given PUID from the image list """
        for bundle in self.bundleList:
            if puid == bundle.PUID:
                return bundle.images
        return None

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
        rows =[]
        for bundle in self.bundleList:
            images = ""
            for i in bundle.images:
                images = images + i + ","
            rows.append([bundle.PUID, 0, images])
        sql.executemany("INSERT OR IGNORE INTO unlabelledParts(puid, user, images) VALUES (?, ?, ?)", rows)
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
                sql.execute("DELETE FROM unlabelledParts WHERE puid = ?", [row[0]])
        sql.commit()

    @staticmethod
    def RowToBundle(row: List):
        # DB rows unpack into ImageBundle members: row[0] = puid, row[1] = user, row[2] = images
        images = row[2].split(',')
        images = list(filter(None, images))
        return ImageBundle(images, row[0], row[1], "")

    def __ClaimBundle__(self, bundle: ImageBundle, user: int):
        """ Changes ownership of a bunbdle in the parts db"""
        if bundle is None:
            return
        sql = sqlite3.connect(self.mainDB)
        sql.execute("UPDATE unlabelledParts SET user = ? WHERE puid = ?", [str(user), bundle.puid])
        sql.commit()

    def GetImageBundle(self, user):
        """
        Gets an image bundle from the database. If the user has a bundle already assigned to them, it will be fetched.
        Otherwise, the user gets a new bundle from the database.

         DB rows unpack into ImageBundle members: row[0] = puid, row[1] = user, row[2] = images
        """
        # No user should have id 0; It represents parts that have not been assigned to a user
        if user == 0:
            return None

        sql = sqlite3.connect(self.mainDB)
        cursor = sql.cursor()
        cursor.execute("SELECT * FROM unlabelledParts WHERE user = ? LIMIT 1", str(user))
        row = cursor.fetchall()
        if len(row) < 1:
            # The user should get a new unlabelled part
            cursor.execute("SELECT * FROM unlabelledParts WHERE user = 0 LIMIT 1")
            row = cursor.fetchall()
            if len(row) < 1:
                # No images left!
                return None
            # claim a bundle
            bundle = self.RowToBundle(row[0])
            self.__ClaimBundle__(bundle, user)
            return bundle
        else:
            # The user has a part already assigned to them
            return self.RowToBundle(row[0])

    def __RemoveBundleFromDB__(self, bundle: ImageBundle):
        sql = sqlite3.connect(self.mainDB)
        sql.execute("DELETE FROM unlabelledParts WHERE puid = ?", [bundle.PUID])
        sql.commit()

    def __LogBundle__(self, bundle):
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

    def __SkipImageBundle__(self, bundle: ImageBundle):
        """ A user skipped an image bundle """
        # TODO: Implement the bounty system for skipping parts
        self.__ClaimBundle__(bundle, -1)

    def __BadImages__(self, bundle: ImageBundle):
        """ Handle pictures of different parts or poorly cropped """
        fu.HandleBadImages(bundle)
        self.__RemoveBundleFromDB__(bundle)

    def __ConveyorImage__(self, bundle: ImageBundle):
        """ Handle pictures of the conveyor belt """
        fu.HandleBadImages(bundle)
        self.__RemoveBundleFromDB__(bundle)

    def HandleBadImages(self, puid:str, type: str):
        """
        Bad image types:
            conveyor - a picture of the conveyor belt
            badImages - pictures of different parts or pooryl cropped
            skip - a picture was skipped.
        """
        bundle = self.__FindBundleFromPUID__(puid)
        if bundle is None:
            return

        if type == "conveyor":
            self.__ConveyorImage__(bundle)

        if type == "badImages":
            self.__BadImages__(bundle)

        if type == "skip":
            self.__SkipImageBundle__(bundle)


imageMgr = ImageManager(cu.settings)
