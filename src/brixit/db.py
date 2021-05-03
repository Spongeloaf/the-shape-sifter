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


def MoveFiles(form: dict):
    """ Moves an image or a bundle of images from the new parts folder to a training folder """

    with open(cu.settings.knownPartsDb, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter='\t')
        images = cu.ImageStrToList(form['images'])
        for i in images:
            srcPath = cu.settings.unknownPartsPath + "\\" + i
            dstPath = cu.settings.knownPartsPath + "\\" + i
            try:
                os.replace(srcPath, dstPath)
            except Exception as e:
                continue
            row = [i, form['partNumber']]
            writer.writerow(row)

    return "success"


def LogPartMoved(form):
    """ Logs a successful part move in the user database """

    return "success"

def SubmitPart(form: dict):
    """ Submits a part to the sorting database. This involves moving the file and logging the action. """
    result = MoveFiles(form)
    if result != "success":
        return result

    return LogPartMoved(form)



