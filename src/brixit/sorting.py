from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for)

from auth import login_required
import commonUtils as cu
import os
import db as dataBase


bp = Blueprint('sorting', __name__)
mediaFolder = cu.GetGoogleDrivePath() + "\\assets\\photophile\\new_part_images"


def HandlePost(request, images):
    """
    Handle the various types of POST events.
    """

    if 'submit' in request.form:
        # TODO: Handle part submissions here!
        flash("Submitted!")
        return render_template('sorting/sorting.html', images=images)

    if 'query' in request.form:
        query = request.form['query']
        return render_template('sorting/sorting.html', images=images, query=query)

    flash("HandlePost() got no query or submission")
    return render_template('sorting/sorting.html', images=images)


@bp.route('/<path:filename>')
def download_file(filename):
    return send_from_directory(mediaFolder, filename, as_attachment=True)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def sorting(query=None):
    """
    This page presents an image or list of images to the user. It will then ask them to try and identify the part
    by name and show a list of suggested names from the parts db.

    This version contains search results.
    TODO: This may become problematic once we have multiple users.
    TODO: It is quite possible that while searching another user may delete the picture you're looking at.
    """
    assetfolder = cu.GetGoogleDrivePath()
    srcImageFolder = assetfolder + "\\assets\\photophile\\new_part_images"
    walker = os.walk(srcImageFolder, topdown=False)
    images = cu.GetImageBundle(walker)

    if request.method == 'POST':
        return HandlePost(request, images)

    return render_template('sorting/sorting.html', images=images)

