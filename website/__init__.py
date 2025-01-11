import os, importlib
import threading

from flask import Flask,render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from werkzeug.security import generate_password_hash

# from website.static_loader import download_static_files
# download_static_files()

db:sqlalchemy = SQLAlchemy()
DB_NAME  = 'database.db'

socketio = SocketIO()


def create_database(app):
    with app.app_context():
        db.create_all()
    print("Database created")


def create_app(crawling:bool = False):
    
    app = Flask(__name__)
    # app.config['SECRET_KEY'] = "NONEEDSECRETKEY"
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)

    blueprints = ['views']
    for i in blueprints:
        bp = importlib.import_module(f'website.{i}', 'bp').bp
        app.register_blueprint(bp)

    create_database(app)

    from website.crawl import interval
    if crawling:
        threading.Thread(target=interval, args=[app], daemon=True).start()

    socketio.init_app(app)
    return app
