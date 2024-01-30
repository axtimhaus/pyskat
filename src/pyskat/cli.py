from pathlib import Path

import click
import click_repl

from .tournament import Tournament

APP_DIR = Path(click.get_app_dir("pyroll"))
DEFAULT_HISTORY_FILE = APP_DIR / "shell_history"

from rich import get_console

console = get_console()

from rich.traceback import install

SUPPRESS_TRACEBACKS = [
    click
]

install(
    console=console,
    show_locals=False,
    suppress=SUPPRESS_TRACEBACKS
)


@click.group()
@click.pass_context
def main_group(ctx):
    ctx.obj = Tournament


@main_group.command()
@click.option(
    "--history-file",
    help="File to read/write the shell history to.",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_HISTORY_FILE, show_default=True
)
@click.pass_context
def shell(ctx, history_file):
    """Opens a shell or REPL (Read Evaluate Print Loop) for interactive usage."""

    @click.command
    def exit():
        """Exits the shell or REPL."""
        click_repl.exit()

    main_group.add_command(exit)

    console.print(
        "Launching interactive shell mode.\n"
        "Enter PySkat CLI subcommands as you wish, state is maintained between evaluations.\n"
        "Global options (-c/--config-file, -C/--global-config, -p/--plugin, ...) do [b]not[/b] work from here, "
        "specify them when lauching `pyskat shell`.\n\n"
        "Type [b]--help[/b] for help on available subcommands.\n"
        "Type [b]exit[/b] to leave the shell.",
        highlight=False
    )

    from prompt_toolkit.history import FileHistory
    prompt_kwargs = dict(
        history=FileHistory(str(history_file.resolve())),
        message=[("bold", "\npyskat ")]
    )
    click_repl.repl(ctx, prompt_kwargs=prompt_kwargs)
