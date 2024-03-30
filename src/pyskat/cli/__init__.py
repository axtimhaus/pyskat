from . import evaluate_commands, player_commands, result_commands, series_commands, shell, wui
from .main import main

main.add_command(shell.shell)
main.add_command(player_commands.player)
main.add_command(result_commands.result)
main.add_command(evaluate_commands.evaluate)
main.add_command(series_commands.series)
main.add_command(wui.wui)
