from flask import render_template
from . import appbuilder

"""
    403 error handler
"""
@appbuilder.app.errorhandler(403)
def page_not_found1(e):
    return (
        render_template(
            "403.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        403,
    )

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
"""
    500 error handler
"""
@appbuilder.app.errorhandler(500)
def internal_server_error(e):
    return (
        render_template(
            "500.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        500,
    )    
"""
    unhandled_exception
"""
@appbuilder.app.errorhandler(Exception)
def unhandled_exception(e):
    return (
        render_template(
            "500.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        500,
    )        