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


def MoveFiles(bundle: cu.ImageBundle):
    """ Moves an image or a bundle of images from the new parts folder to a training folder """
    # TODO: When we add logging, then the retrun of __MoveImages__() may be interesting to log.
    with open(cu.settings.labelledPartsTxt, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter='\t')
        for i in bundle.images:
            srcPath = cu.settings.unlabelledPartsPath + "\\" + i
            dstPath = cu.settings.labelledPartsPath + "\\" + i
            if __MoveImages__(srcPath, dstPath):
                row = [i, bundle.partNum]
                writer.writerow(row)


def __MoveImages__(src: str, dst: str):
    try:
        os.replace(src, dst)
        return True
    except Exception as e:
        print("Tried to move a file in fileUtils.py::MoveImages() but got an exception: " + str(e))
        return False


def HandleBadImages(imagesStr : str, reason: str):
    images = cu.ImageStrToList(imagesStr)
    if reason == 'conveyor':
        for i in images:
            srcPath = cu.settings.unlabelledPartsPath + "\\" + i
            dstPath = cu.settings.conveyorBeltImgFolder + "\\" + i
            __MoveImages__(srcPath, dstPath)
        return

    if reason == 'badImages':
        for i in images:
            os.remove(cu.settings.unlabelledPartsPath + "\\" + i)

    if reason == 'skip':
        for i in images:
            srcPath = cu.settings.unlabelledPartsPath + "\\" + i
            dstPath = cu.settings.skippedImageFolder + "\\" + i
            __MoveImages__(srcPath, dstPath)
