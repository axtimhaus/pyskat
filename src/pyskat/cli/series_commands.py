from typing import Optional

import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe


@click.group()
def series():
    """Generate and manage game series."""
    pass


@series.command()
@pass_backend
def generate(backend: Backend):
    """Generate a random player distribution of players to tables."""
    shuffle = backend.generate_series()
    print_pandas_dataframe(shuffle)
