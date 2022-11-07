try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")

import os
from threading import Thread
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
import panel as pn
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import sockets,app,apps



def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())
    bokeh_tornado = BokehTornado(
        apps, extra_websocket_origins=["127.0.0.1:8000"]
    )
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
    print("    gunicorn -w 4 run:app --reload")
    print()
    print("will start the app on four processes")
    app.run(host="0.0.0.0", port=8000, debug=True)
    import sys

    sys.exit()


# pn.serve(apps,
#         port=8000, allow_websocket_origin=["127.0.0.1:8000"],
#          address="127.0.0.1", show=False)