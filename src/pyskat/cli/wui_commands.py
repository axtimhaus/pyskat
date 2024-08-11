from pathlib import Path

import click

from pyskat.backend import Backend
from pyskat.cli.config import APP_DIR
from pyskat.cli.main import pass_backend
from pyskat.wui.app import create_app


instance_path_option = click.option(
    "-p",
    "--instance-path",
    default=APP_DIR,
    type=click.Path(exists=True, file_okay=False, writable=True, path_type=Path),
    help="The instance path to read config from an store state information to.",
)


@click.group()
def wui():
    """Run and manage the WebUI of PySkat."""


@wui.command()
@instance_path_option
@pass_backend
def run(
    backend: Backend,
    instance_path: Path,
):
    app = create_app(backend, instance_path)
    app.run()


@wui.command()
@instance_path_option
def create_config(instance_path: Path):
    pass
