from pathlib import Path

import click
import click_repl

from ..rich import console
from .config import APP_DIR
from .main import main

DEFAULT_HISTORY_FILE = APP_DIR / "shell_history"


@click.command()
@click.option(
    "--history-file",
    help="File to read/write the shell history to.",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_HISTORY_FILE,
    show_default=True,
)
@click.pass_context
def shell(ctx, history_file: Path):
    """Opens a shell or REPL (Read Evaluate Print Loop) for interactive usage."""

    @click.command
    def exit():
        """Exits the shell or REPL."""
        click_repl.exit()

    main.add_command(exit)

    console.print(
        "Launching interactive shell mode.\n"
        "Enter PySkat CLI subcommands as you wish, state is maintained between evaluations.\n"
        "Global options (-f/--database-file, ...) do [b]not[/b] work from here, "
        "specify them when launching `pyskat shell`.\n\n"
        "Type [b]--help[/b] for help on available subcommands.\n"
        "Type [b]exit[/b] to leave the shell.",
        highlight=False,
    )

    from prompt_toolkit.history import FileHistory

    prompt_kwargs = dict(
        history=FileHistory(str(history_file.resolve())),
        message=[("bold", "\npyskat ")],
    )
    click_repl.repl(ctx, prompt_kwargs=prompt_kwargs)
