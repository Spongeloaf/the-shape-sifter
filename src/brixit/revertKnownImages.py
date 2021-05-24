import commonUtils as cu
import os


def RevertFolder(src, dst):
    """ Moves the contents of a folder from one place to another """
    walker = os.walk(src, topdown=False)
    for root, dirs, files in walker:
        for file in files:
            srcPath = os.path.join(root, file)
            dstPath = os.path.join(dst, file)
            try:
                os.replace(srcPath, dstPath)
            except Exception as e:
                continue


def RevertUnknownFiles():
    """ Moves files from the unknown folder back to the known folder and erases knownparts.txt """
    folders = [
        cu.settings.TXT_labelLog,
        cu.settings.fakeDeleteFolder,
        cu.settings.conveyorBeltImgFolder,
        cu.settings.skippedImageFolder
    ]

    for folder in folders:
        RevertFolder(folder, cu.settings.unlabelledPartsPath)

    if os.path.exists(cu.settings.TXT_labelLog):
        os.remove(cu.settings.TXT_labelLog)


if __name__ == "__main__":
    RevertUnknownFiles()
