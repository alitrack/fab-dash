from flask_appbuilder.baseviews import BaseView
from flask_appbuilder import expose, has_access

from . import appbuilder,port,apps

from bokeh.embed import  server_session
from bokeh.client import pull_session

class DashboardView(BaseView):
    route_base = "/"
    @has_access
    @expose("/dashboard/<app>")
    def methoddash(self, app):
        url = f"http://127.0.0.1:{port}/{app}"
        with pull_session(url=url) as session:
            # generate a script to load the customized session
            script = server_session(session_id=session.id, url=url)
            # script = server_document(url)
        return self.render_template("dash.html", script=script, appbuilder=appbuilder)    

appbuilder.add_view_no_menu(DashboardView())

for key in apps:
    key = key[1:]
    appbuilder.add_link(
        key, href=f"/dashboard/{key}", icon="fa-list",category="Dashboard", category_icon="fa-list"
    )