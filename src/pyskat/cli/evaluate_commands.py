import click

from .main import pass_backend
from ..backend import Backend
from ..rich import console, print_pandas_dataframe


@click.group()
def evaluate():
    pass


@evaluate.command()
@pass_backend
def results(backend: Backend):
    evaluation = backend.evaluate_results()

    print_pandas_dataframe(evaluation)


@evaluate.command()
@pass_backend
def total(backend: Backend):
    evaluation = backend.evaluate_total()

    for ind in evaluation.columns.levels[0]:
        if isinstance(ind, int):
            title = f"Series {ind}"
        elif isinstance(ind, str):
            title = ind.title()
        else:
            title = None

        print_pandas_dataframe(evaluation[ind], title)
