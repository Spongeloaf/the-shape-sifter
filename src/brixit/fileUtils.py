import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import commonUtils as cu
import os
import csv


def MoveFiles(bundle: cu.ImageBundle):
    """
    Moves an image or a bundle of images from the new parts folder to a training folder.
    Returns False if any file fails to move
    """
    result = True
    with open(cu.settings.TXT_labelLog, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter='\t')
        for i in bundle.images:
            srcPath = cu.settings.unlabelledPartsPath + "/" + i
            dstPath = cu.settings.labelledPartsPath + "/" + i
            if __MoveImages__(srcPath, dstPath):
                row = [i, bundle.partNum]
                writer.writerow(row)
            else:
                result = False
    return result


def __MoveImages__(src: str, dst: str):
    try:
        os.replace(src, dst)
        return True
    except Exception as e:
        print("Tried to move a file in fileUtils.py::MoveImages() but got an exception: " + str(e))
        return False


def HandleConveyorImages(bundle: cu.ImageBundle):
    result = True
    for i in bundle.images:
        srcPath = cu.settings.unlabelledPartsPath + "/" + i
        dstPath = cu.settings.conveyorBeltImgFolder + "/" + i
        if not __MoveImages__(srcPath, dstPath):
            result = False
    return result


def __DeleteFile__(file: str):
    """ Wrapper to allow real or fake deletion of files. Fake deleted files are just moved to another folder. """
    if cu.settings.fakeDeleteFiles:
        dstPath = cu.settings.fakeDeleteFolder + "/" + os.path.split(file)[1]
        __MoveImages__(file, dstPath)
    else:
        os.remove(file)


def HandleBadImages(bundle: cu.ImageBundle):
    """ Removes unwanted image files. Returns false if any file cannot be found. """
    result = True
    for i in bundle.images:
        file = cu.settings.unlabelledPartsPath + "/" + i
        if not os.path.isfile(file):
            result = False
        __DeleteFile__(file)
    return True


# Everything below this line came from the flask tutorial
def GetDb():
    if 'db' not in g:
        g.db = sqlite3.connect(
            cu.settings.DB_User,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def CloseDb(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def InitDb():
    db = GetDb()

    with current_app.open_resource('BriXit_schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def InitDbCommand():
    """Clear the existing data and create new tables."""
    InitDb()
    click.echo('Initialized the database.')


def InitApp(app):
    app.teardown_appcontext(CloseDb)
    app.cli.add_command(InitDbCommand)
