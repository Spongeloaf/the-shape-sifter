#####################################################################
# This web application allows a user classify images of lego parts
# The classified pictures will be prepped for ai training and
# placed into the appropriate folder.
#####################################################################

import sys
import db
from flask import Flask
from commonUtils import GetGoogleDrivePath


assetPath = GetGoogleDrivePath()
sourceImagePath = assetPath + "\\assets\\photophile\\new_part_images"
instancePath = assetPath + "\\briXit"
DbPath = sys.path[0] + '\\briXit.sqlite'


def create_app():
    # create and configure the app
    app = Flask(__name__,instance_path=instancePath)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=DbPath,
    )

    app.config.from_pyfile('config.py', silent=True)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)

    import auth
    app.register_blueprint(auth.bp)

    import sorting
    app.register_blueprint(sorting.bp)
    app.add_url_rule('/', endpoint='index')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
