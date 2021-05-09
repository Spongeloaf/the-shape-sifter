import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import commonUtils as cu
import os
import csv


def GetDb():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
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


def MoveFiles(part: cu.Part):
    """ Moves an image or a bundle of images from the new parts folder to a training folder """

    with open(cu.settings.knownPartsDb, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter='\t')
        images = cu.ImageStrToList(part.realImageListStr)
        for i in images:
            srcPath = cu.settings.unknownPartsPath + "\\" + i
            dstPath = cu.settings.knownPartsPath + "\\" + i
            if MoveImages(srcPath, dstPath):
                row = [i, part.partNum]
                writer.writerow(row)

    return "success"


def LogPartMoved(part: cu.Part, user: int):
    """ Logs a successful part move in the user database """
    # TODO: Need to track which users move a file!
    return "success"


def SubmitPart(part: cu.Part, user: int):
    """ Submits a part to the sorting database. This involves moving the file and logging the action. """
    result = MoveFiles(part)
    if result != "success":
        return result

    return LogPartMoved(part, user)


def MoveImages(src: str, dst: str):
    try:
        os.replace(src, dst)
        return True
    except Exception as e:
        print("Tried to move a file in db.py::MoveImages() but got an exception: " + str(e))
        return False


def HandleBadImages(imagesStr : str, reason: str):
    images = cu.ImageStrToList(imagesStr)
    if reason == 'conveyor':
        for i in images:
            srcPath = cu.settings.unknownPartsPath + "\\" + i
            dstPath = cu.settings.conveyorBeltImgFolder + "\\" + i
            MoveImages(srcPath, dstPath)
        return

    if reason == 'badImages':
        for i in images:
            os.remove(cu.settings.unknownPartsPath + "\\" + i)

    if reason == 'skip':
        for i in images:
            srcPath = cu.settings.unknownPartsPath + "\\" + i
            dstPath = cu.settings.skippedImageFolder + "\\" + i
            MoveImages(srcPath, dstPath)
