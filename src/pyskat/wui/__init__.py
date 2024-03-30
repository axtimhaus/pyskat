from flask import Flask

from ..cli.main import main
from . import index
from . import players


@main.command()
def wui():
    from .app import app

    app.run(debug=True)
