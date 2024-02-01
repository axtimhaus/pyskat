# PySkat - A simple CLI and TUI Skat Tournament Management Program

PySkat is a simple tool for managing tournaments of the German national card game Skat.
The functionality follows the [official tournament rules](https://dskv.de/app/uploads/sites/43/2022/11/ISkO-2022.pdf) given by the [Deutscher Skatverband e.V.](https://dskv.de) (German Skat Association).
Evaluation of games is oriented at the [official game sheets](https://dskv.de/app/uploads/sites/43/2020/11/Spiellisten.pdf) for tournaments.

# Current Status

This software is currently in **alpha** state, thus is functionality is not complete and the API may or will change in future.

The following features are already working:

- TinyDB backend with API methods to create, update, get and list players and game results.
- Backend function to automatically evaluate game results according to official tournament rules.
- CLI to interact with the backend database.

The following planned features are **not** working:

- CLI to shuffle players to tables and evaluate game results.
- TUI interface with same feature set as the CLI.

# Installation

> [!NOTE]
> The software is currently not published on PyPI, but will be after the first alpha version is finished.

# Usage

Once installed, run the CLI using the `pyskat` command.

To show the help on available commands run:

```shell
pyskat --help
```

You may use all commands directly from your preferred command line.
However, it is recommended to open the interactive shell of PySkat, as this saves typing and provides syntax completion without configuring your shell.
To open an interactive shell use:

```shell
pyskat shell
```

By default, a file named `pyskat_db.json` is created in the current working directory holding the persistent data of players and results.
You may specify another file by the `-f/--database-file` option, for example:

```shell
pyskat -f my_first_tournament.json shell
```

Players are managed using the `player` command and its subcommands, results using the respective `result` command.
Data for each command can be specified using options, or, if omitted are prompted.
To get help on a specific command use the `-h/--help` option on that commands, like:

```shell
pyskat player add --help
```

# License

This software is published under the terms of the [MIT License](LICENSE).

# Contributing

This project is in early status and does currently not accept code contributions.
This may change in future.
Feedback and suggestions are welcome via issues.