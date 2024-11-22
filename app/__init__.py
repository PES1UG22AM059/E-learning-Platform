from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from config import Config

# Initialize MySQL
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mysql.init_app(app)

    # Register the main blueprint
    from .routes import main
    app.register_blueprint(main, url_prefix='/')

    # The '/enrollment' route is no longer necessary, as enrollment happens via courses.html
    # Hence, we do not define it here. All enrollment functionality is handled by the '/enroll' route
    # defined in the routes.py file.

    return app
