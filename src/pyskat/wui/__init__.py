from .app import app
from . import index
from . import players
from . import series


def run_wui():

    app.run(debug=True)


if __name__ == "__main__":
    run_wui()
