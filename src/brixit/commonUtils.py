import os


def GetGoogleDrivePath():
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

    root1, ext1 = os.path.split(f1)
    root2, ext2 = os.path.split(f1)

    if (ext1 != ".png") and (ext2 != ".png"):
        return False

    haystack1 = root1.split('_')
    haystack2 = root2.split('_')

    # Length will be 2 as long as the filename has only one '_' somewhere inside it.
    if (len(haystack1) != 2) or (len(haystack2) != 2):
        return False

    # Ensure both indexes are integers
    try:
        i1 = int(haystack1)
        i2 = int(haystack2)
    except:
        return False

    if haystack1[0] == haystack2[0]:
        # If we've made it this far, then both files are from the same bundle and have different indexes.
        return True

    return False


def GetImageBundle(walker):
    """ Gets the first file from a directory and tries to find any files from the same bundle """
    try:
        for root, dirs, files in walker:
            # Grab the first file in the directory
            selectedFile = files.pop(0)

            fileStr = selectedFile.split('.')
            if fileStr[1] != "png":
                continue

            imageBundle = [selectedFile]

            # Images may be standalone or part of a bundle.
            # Bundled images are in the same folder, add them.
            for f in files:
                if AreFilesInABundle(selectedFile, f):
                    imageBundle.append(f)

            return imageBundle

    except Exception as e:
        print("Python Error in GetImageBundle()" + e)
        return None
