import commonUtils as cu
import random
import string
import Constants as k
import sqlite3
from sqlite3 import Error
import os
from pathlib import Path
import uuid


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


def GenerateSerial():
    """ Creates a serial key for a new user and inserts it into the database """
    key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(k.kSerialLength))
    sql = sqlite3.connect(cu.settings.DB_User)
    if sql.execute('SELECT serialKey FROM keys WHERE serialKey = ?', [key]).fetchone() is not None:
        print("Error: Serial key in use!")
        return

    sql.execute('INSERT INTO keys (serialKey) VALUES (?)', [key])
    sql.commit()
    print("Here is your new serial key:")
    print(key)


def create_BriXit_db(db_file, schema):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Sqlite version: " + sqlite3.version)
        print("Filename: " + str(db_file))

        f = open(schema)
        conn.executescript(f.read())

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def ScrambleUnlabelledImages():
    """
    A dangerous function that randomizes filenames in the unlabelled parts folder with 12 characcter GUID names.
    WARNING: THIS FUNCTION DESTROYS IMAGE BUNDLES! USE AT YOUR OWN RISK!
    """
    walker = os.walk(cu.settings.unlabelledPartsPath, topdown=False)
    for root, dirs, files in walker:
        for file in files:
            newName = str(uuid.uuid4())[:12] + ".png"
            src = Path(root) / file
            dst = Path(root) / newName
            os.rename(src, dst)


if __name__ == '__main__':
    while True:
        x = int(input("Enter a number:\r\n0: New serial key\r\n1: Create part DB\r\n2: Create log DB\r\n3: Create user DB\r\n4: Reset labelled images\r\n5: Exit\r\n"))

        if x == 0:
            GenerateSerial()

        if x == 1:
            y = int(input("Are you sure you want to reset the unlabelled part database?\r\nPlease enter '9' to confirm!"))
            if y == 9:
                create_BriXit_db(cu.settings.DB_Parts, "partsSchema.sql")

        if x == 2:
            y = int(input("Are you sure you want to reset the log database?\r\nPlease enter '9' to confirm!"))
            if y == 9:
                create_BriXit_db(cu.settings.DB_LabelLog, "logSchema.sql")

        if x == 3:
            y = int(input("Are you sure you want to reset the user database?\r\nPlease enter '9' to confirm!"))
            if y == 9:
                create_BriXit_db(cu.settings.DB_User, "userSchema.sql")

        if x == 4:
            y = int(input("Are you sure? This will undo all of your labelling progress!!\r\nPlease enter '9' to confirm!"))
            if y == 9:
                RevertUnknownFiles()

        if x == 5:
            break
