from .main import main
from . import shell
from . import player_commands

main.add_command(shell.shell)
main.add_command(player_commands.player)
