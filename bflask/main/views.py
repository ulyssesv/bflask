from flask import current_app, redirect
from . import main


@main.route('/')
def index():
    return redirect(current_app.config['SITE_INDEX'])
