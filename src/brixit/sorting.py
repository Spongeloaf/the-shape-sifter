from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for)

from auth import login_required
import commonUtils as cu
import os
import db as dataBase


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

    # if len(images) < 1:
    #     # TODO: need to make an "out of files" page
    #     return render_template('sorting/sorting.html', images=images)

    if request.method == 'POST':
        if 'partNumber' in request.form:
            result = dataBase.SubmitPart(request.form)
            images = cu.GetImageBundle(walker)
            if result == "success":
                partNumber = request.form['partNumber']
                flash("Submitted {} as {}".format(cu.GetPUID(images[0]), partNumber))
                return render_template('sorting/sorting.html', images=images)
            else:
                flash("Error in part submission: {}".format(result))
                return render_template('sorting/sorting.html', images=images)

        if 'query' in request.form:
            query = request.form['query']

            res1 = Result()
            res1.label = "2x4 brick"
            res1.partNumber = "2004"
            res2 = Result()
            res2.label = "1x3 plate"
            res2.partNumber = "1003"
            res3 = Result()
            res3.label = "1x9 tile"
            res3.partNumber = "1009"
            results = [res1,res2,res3]
            return render_template('sorting/sorting.html', images=images, results=results)

        flash("HandlePost() got no query or submission")
        return render_template('sorting/sorting.html', images=images)

    # request.method == 'Get':
    return render_template('sorting/sorting.html', images=images)

