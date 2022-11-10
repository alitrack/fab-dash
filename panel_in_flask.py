try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")
# import os
# os.environ['PANEL_NPM_CDN']='https://cdn.jsdelivr.net/npm'
from threading import Thread
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from bokeh.server.util import bind_sockets

from bokeh.embed import  server_session
from bokeh.client import pull_session

from bokeh.application import Application
from bokeh.application.handlers  import   CodeHandler



from flask import Flask,render_template_string
app = Flask(__name__)


sockets, port = bind_sockets("127.0.0.1", 0)

def get_source():
    with open('/Users/steven/workspace/tmp/xx.py') as f:
        return f.read()

@app.get("/code")
def get_code():
    with open('apps/button.py') as f:
        return f.read() 

str ="""
import panel as pn
text = pn.widgets.TextInput(value='Ready')

def b(event):
    text.value = 'Clicked {0} times'.format(button.clicks)
button = pn.widgets.Button(name='Click me', button_type='primary')    
button.on_click(b)
column = pn.Row(button, text)
column.servable()
"""
demo_app  = Application(CodeHandler(source = get_source(),
filename="xx.py"
))

apps = {}
apps['/demo'] =demo_app
@app.get("/")
def flask_page():
    html = []
    html.append("<h1>Panel Demo</h1>")
    for key in apps:
        html.append(f"<a href='panel{key}'>{key[1:]}</a>")
    return "<br>".join(html)

@app.get("/panel/<app>")
def panel_page(app):
    bokeh_tornado.applications[app] = demo_app
    url = f"http://127.0.0.1:{port}/{app}"
    with pull_session(url=url) as session:
        # generate a script to load the customized session
        script = server_session(session_id=session.id, url=url)
    return render_template_string("<body>{{script|safe}}</body>", script=script)



bokeh_tornado = BokehTornado(
    apps, extra_websocket_origins=["127.0.0.1:8000"]
) 
def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())

    bokeh_tornado.applications
    bokeh_http = HTTPServer(bokeh_tornado)
    bokeh_http.add_sockets(sockets)

    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()


t = Thread(target=bk_worker)
t.daemon = True
t.start()


if __name__ == "__main__":
    print("This script is intended to be run with gunicorn. e.g.")
    print()
    print("    gunicorn -w 4 panel_in_flask:app --reload")
    print()
    print("will start the app on four processes")
    app.run(host="0.0.0.0", port=8000, debug=True)