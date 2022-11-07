import logging
from glob import glob

from bokeh.server.util import bind_sockets
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from bokeh.command.util import build_single_handler_applications
"""
 Logging configuration
"""
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

sockets, port = bind_sockets("127.0.0.1", 0)

files = glob("apps/*.py")
apps = build_single_handler_applications(files)
from . import views, error_handler  # noqa
