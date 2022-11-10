import panel as pn
from flask import Flask

flask_app = Flask(__name__)

@flask_app.route('/app')
def hello_world():
    return 'Hello, World!'

def panel_app():
    return "# This Panel app runs alongside flask, access the flask app at [here](./flask/app)"

pn.serve({'/flask': flask_app, 'panel': panel_app}, port=5001)