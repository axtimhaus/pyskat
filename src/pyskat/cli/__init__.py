from .main import main
from . import shell
from . import player_commands
from . import result_commands

main.add_command(shell.shell)
main.add_command(player_commands.player)
main.add_command(result_commands.result)
