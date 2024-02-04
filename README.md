# PySkat - A simple CLI and TUI Skat Tournament Management Program

PySkat is a simple tool for managing tournaments of the German national card game Skat. The functionality follows
the [official tournament rules](https://dskv.de/app/uploads/sites/43/2022/11/ISkO-2022.pdf) given by
the [Deutscher Skatverband e.V.](https://dskv.de) (German Skat Association). Evaluation of games is oriented at
the [official game sheets](https://dskv.de/app/uploads/sites/43/2020/11/Spiellisten.pdf) for tournaments.

## Current Status

This software is currently in **alpha** state, thus is functionality is not complete and the API may or will change in
future.

The following features are already working:

- TinyDB backend with API methods to create, update, get and list players and game results.
- Backend function to automatically evaluate game results according to official tournament rules.
- CLI to interact with the backend database.
- CLI to shuffle players to tables and evaluate game results.

The following planned features are **not** working:

- TUI interface with same feature set as the CLI.
- HTML printout of players, series, results.

## Installation

The software is published on PyPI and can be installed via `pip` or similar tools:

```shell
pip install pyskat
```

## Usage

Once installed, run the CLI using the `pyskat` command.

To show the help on available commands run:

```shell
pyskat --help
```

You may use all commands directly from your preferred command line. However, it is recommended to open the interactive
shell of PySkat, as this saves typing and provides syntax completion without configuring your shell. To open an
interactive shell use:

```shell
pyskat shell
```

By default, a file named `pyskat_db.json` is created in the current working directory holding the persistent data of
players and results. You may specify another file by the `-f/--database-file` option, for example:

```shell
pyskat -f my_first_tournament.json shell
```

### Managing Players

Players are managed using the `player` command and its subcommands. Data for each command can be specified using
options, or, if omitted are prompted. To get help on a specific command use the `-h/--help` option on that command,
like:

```shell
pyskat player --help
```

To add a new player:

```shell
pyskat player add
```

To list all players in database:

```shell
pyskat player list
```

To update an existing player:

```shell
pyskat player update
```

To remove a player:

```shell
pyskat remove
```

### Generating a Series

To distribute players randomly to tables (generating a series), use the `series generate` command. This will print out a
data sheet indexed by table ID with players placed at the tables, so that the current number of players in the database
is efficiently distributed to four- and three-player tables.

```shell
pyskat generate series
```

### Entering Results

Results are managed using the `result` command and its subcommands. Data for each command can be specified using
options, or, if omitted are prompted.
A result is meant as the result of a specific player in a specific series.

To add a new result:

```shell
pyskat result add
```

To list all results in database:

```shell
pyskat result list
```

To update an existing result:

```shell
pyskat result update
```

### Evaluating Results

Results over all games can be evaluated using the `evaluate` command. For example to generate the high-score list of the
tournament, execute:

```shell
pyskat evaluate total -s score
```

# License

This software is published under the terms of the [MIT License](LICENSE).

# Contributing

This project is in early status and does currently not accept code contributions. This may change in future. Feedback
and suggestions are welcome via issues.