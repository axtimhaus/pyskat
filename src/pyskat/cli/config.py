from pathlib import Path

import click

APP_DIR = Path(click.get_app_dir("pyskat"))

APP_DIR.mkdir(exist_ok=True)
