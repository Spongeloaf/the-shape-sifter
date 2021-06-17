from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for, session)
from auth import login_required
import commonUtils as cu
import os
import partIndex as pi
import imageManager as im
import Constants as k


bp = Blueprint('labelling', __name__)


class Result:
    partNumber = ""
    label = ""


def Error(text :str):
    """ Handler for error messages that lets us deliver them wherever we'd like """
    print(text)
    flash(text)


@bp.route('/<path:filename>')
def GetUnknownImage(filename):
    return send_from_directory(cu.settings.unlabelledPartsPath, filename, as_attachment=True)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def labelling(query=None):
    """
    This page presents an image or list of images to the user. It will then ask them to try and identify the part
    by name and show a list of suggested names from the parts db.
    """
    user_id = session["user_id"]
    results = []

    if request.method == 'POST':
        # label submission
        if 'partNum' in request.form:
            formBundle = im.MakeBundleFromForm(request.form, user_id)
            if formBundle is not None:
                im.imageMgr.LabelImageBundle(formBundle)
                print("Part {} labelled by {}".format(formBundle.PUID, str(formBundle.user)))
            else:
                Error("Error in part submission: formBundle was 'None' instead of 'ImageBundle'")

        # Search
        elif 'query' in request.form:
            query = request.form['query']
            results = pi.PartIndex.search(query)
            if len(results) > cu.settings.numberOfResults:
                del results[cu.settings.numberOfResults:]

        # Problem submission; Bad picture, conveyor belt, skipped, etc.
        elif 'problem' in request.form and 'puid' in request.form:
            formBundle = im.MakeBundleFromForm(request.form, user_id)
            if formBundle is not None:
                if not im.imageMgr.HandleBadImages(formBundle, request.form['problem']):
                    Error("Failed to handle a bad image bundle. Problem: {}".format(request.form['problem']))
            else:
                Error("HandlePost() had malformed problem submission")
        else:
            Error("HandlePost() got no query or submission")

    bundle = im.imageMgr.GetImageBundle(user_id)

    if bundle is None:
        return render_template('labelling/labelling.html', images=[], results=results, puid="", k=k)

    return render_template('labelling/labelling.html', images=bundle.images, results=results, puid=bundle.PUID, k=k)
