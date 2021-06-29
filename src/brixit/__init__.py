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
from flask import Flask, render_template
import commonUtils as cu
from gevent.pywsgi import WSGIServer
from auth import login_required
import Constants as k
import DBUtils as DB


def create_app():
    # create and configure the app
    # TODO: Check if I actually need instance path here

    # app = Flask(__name__,instance_path=cu.settings.assetPath)
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=cu.settings.DB_Parts,
    )

    app.config.from_pyfile('config.py', silent=True)


    @app.route('/help')
    @login_required
    def help():
        substitutions = []
        for item in k.kMultiWordSubstitutions.items():
            substitutions.append([item[0], item[1]])
        for item in k.kWordSubstitutions.items():
            substitutions.append([item[0], item[1]])
        for item in k.kCharacterSubstitutions.items():
            substitutions.append([item[0], item[1]])
        return render_template('help.html', substitutions=substitutions)

    @app.route('/scoreboard')
    @login_required
    def scoreboard():
        scores = DB.GetHighScores()
        if scores is None:
            scores = []
        return render_template('scoreboard.html', scores=scores)


    import auth
    app.register_blueprint(auth.bp)

    import labelling
    app.register_blueprint(labelling.bp)
    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == "__main__":
    app = create_app()
    if cu.settings.devMode:
        print("Running in dev mode. Local access only")
        app.run()
    else:
        print("Running in production mode.")
        http_server = WSGIServer((cu.settings.serverIp, cu.settings.serverPort), app)
        print(http_server.address)
        http_server.serve_forever()


