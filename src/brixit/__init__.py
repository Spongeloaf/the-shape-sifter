#####################################################################
# This web application allows a user classify images of lego parts
# The classified pictures will be prepped for ai training and
# placed into the appropriate folder.
#
# This code was largely copied from the Flask tutorial and reworked to suit my needs
# https://flask.palletsprojects.com/en/1.1.x/tutorial/
# Thanks Flask!
#####################################################################


import fileUtils
from flask import Flask
import commonUtils as cu
from gevent.pywsgi import WSGIServer

def create_app():
    # create and configure the app
    # TODO: Check if I actually need instance path here
    # TODO: It's quite possible that this may behave differently if I want to run this from the command line

    app = Flask(__name__,instance_path=cu.settings.assetPath)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=cu.settings.mainDB,
    )

    app.config.from_pyfile('config.py', silent=True)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    fileUtils.InitApp(app)

    import auth
    app.register_blueprint(auth.bp)

    import labelling
    app.register_blueprint(labelling.bp)
    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
    # http_server = WSGIServer(('192.168.0.11', 5000), app)
    # print(http_server.address)
    # http_server.serve_forever()
