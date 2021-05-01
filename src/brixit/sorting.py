from flask import (Blueprint, render_template, send_from_directory)

from auth import login_required
import commonUtils as cu
import os


bp = Blueprint('sorting', __name__)
#MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
mediaFolder = cu.GetGoogleDrivePath() + "\\assets\\photophile\\new_part_images"


@bp.route('/<path:filename>')
def download_file(filename):
    return send_from_directory(mediaFolder, filename, as_attachment=True)

@bp.route('/')
@login_required
def sorting():
    """ This page presents an image or list of images to the user. It will then ask them to try and identify the part
     by name and show a list of suggested names from the parts db. """
    assetfolder = cu.GetGoogleDrivePath()
    srcImageFolder = assetfolder + "\\assets\\photophile\\new_part_images"
    walker = os.walk(srcImageFolder, topdown=False)
    images = cu.GetImageBundle(walker)

    return render_template('sorting/sorting.html', images=images)
