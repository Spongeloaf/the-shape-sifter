from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for)

from auth import login_required
import commonUtils as cu
import os
import db as dataBase
import partIndex as index

bp = Blueprint('sorting', __name__)


class Result:
    partNumber = ""
    label = ""


@bp.route('/<path:filename>')
def download_file(filename):
    return send_from_directory(cu.settings.unknownPartsPath, filename, as_attachment=True)


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
    folder = cu.settings.unknownPartsPath
    walker = os.walk(folder, topdown=False)
    images = cu.GetImageBundle(walker)
    results = []

    # if len(images) < 1:
    #     # TODO: need to make an "out of files" page
    #     return render_template('sorting/sorting.html', images=images)

    if request.method == 'POST':
        if 'partNum' in request.form:
            result = dataBase.SubmitPart(request.form)
            images = cu.GetImageBundle(walker)
            if result == "success":
                partNumber = request.form['partNum']
                # TODO: Nonetype object is not subscriptable
                flash("Submitted {} as {}".format(cu.GetPUID(images[0]), partNumber))
            else:
                flash("Error in part submission: {}".format(result))

        elif 'query' in request.form:
            query = request.form['query']
            results = index.PartIndex.search(query)
            if len(results) > cu.settings.numberOfResults:
                del results[cu.settings.numberOfResults:]
        else:
            flash("HandlePost() got no query or submission")

    # request.method == 'Get' or otherwise:
    return render_template('sorting/sorting.html', images=images, results=results)

