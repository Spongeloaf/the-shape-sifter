from flask import (Blueprint, render_template, send_from_directory, flash, request, redirect, url_for, session)
from auth import login_required
import commonUtils as cu
import os
import partIndex as pi
import imageManager as im


bp = Blueprint('labelling', __name__)


class Result:
    partNumber = ""
    label = ""


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

    # TODO: need to make an "out of files" page
    # TODO: return render_template('labelling/OutOfParts.html')

    user_id = session["user_id"]
    results = []

    if request.method == 'POST':
        # This check is not robust, but it works.
        if 'partNum' in request.form:
            formBundle = im.MakeBundleFromForm(request.form, user_id)
            if formBundle:
                im.imageMgr.LabelImageBundle(formBundle)
            else:
                flash("Error in part submission: {}".format(result))

        elif 'query' in request.form:
            query = request.form['query']
            results = pi.PartIndex.search(query)
            if len(results) > cu.settings.numberOfResults:
                del results[cu.settings.numberOfResults:]

        elif 'problem' in request.form and 'puid' in request.form:
            im.imageMgr.HandleBadImages(request.form['puid'], request.form['problem'])
        else:
            flash("HandlePost() got no query or submission")

    bundle = im.imageMgr.GetImageBundle(user_id)
    if bundle is None:
        # TODO: make an out of parts page and show it here.
        empytImages = []
        emptyPUID = ""
        return render_template('labelling/labelling.html', images=empytImages, results=results, puid=emptyPUID)

    return render_template('labelling/labelling.html', images=bundle.images, results=results, puid=bundle.PUID)
