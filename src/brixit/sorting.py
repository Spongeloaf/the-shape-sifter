from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for, session)
from auth import login_required
import commonUtils as cu
import os
import db as dataBase
import partIndex as pi


bp = Blueprint('sorting', __name__)


class Result:
    partNumber = ""
    label = ""


def FormToPart(form: dict):
    part = cu.Part("", "", "", "", "", "")
    try:
        part.partNum = form['partNum']
        # part.partName = form['partName']
        # part.categoryNum = form['categoryNum']
        # part.categoryName = form['categoryName']
        part.realImageListStr = form['realImage']
        # part.stockImage = form['stockImage']
    except:
        pass
    return part


@bp.route('/<path:filename>')
def GetUnknownImage(filename):
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
    TODO: An idea would be to scan all files before running and make a list of them. When we serve them to
    TODO: a user, we move those filenames (or flag them) as being 'taken', so another user cnnot access
    TODO: them. We'd need to use a lock to ensure that data raaces do not happen. Should be simple enough
    TODO: to implement without needing a lot of rework.
    """


    # TODO: need to make an "out of files" page
    # TODO: return render_template('sorting/OutOfParts.html')

    user_id = session["user_id"]
    results = []

    if request.method == 'POST':
        # This check is not robust, but it works.
        if 'partNum' in request.form:
            partSubmission = FormToPart(request.form)
            result = dataBase.SubmitPart(partSubmission, user_id)
            cu.imageWalker.NewImageBundle()

            if result != "success":
                flash("Error in part submission: {}".format(result))

        elif 'query' in request.form:
            query = request.form['query']
            results = pi.PartIndex.search(query)
            if len(results) > cu.settings.numberOfResults:
                del results[cu.settings.numberOfResults:]

        elif 'badImage' in request.form:
            dataBase.HandleBadImages(request.form['realImage'], request.form['badImage'])
            cu.imageWalker.NewImageBundle()
        else:
            flash("HandlePost() got no query or submission")

    images = cu.imageWalker.GetCurrentImageBundle()
    return render_template('sorting/sorting.html', images=images, results=results)
