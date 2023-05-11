"""This module provides the UDo CLI."""

from pathlib import Path
from typing import List, Optional
import os
import textwrap

import typer

from udo import ERRORS, __app_name__, __version__, config, database, udo
from udo.due_options import due_options

app = typer.Typer()

def due_callback(value: str):
    if value not in due_options.keys():
        raise typer.BadParameter("Not in allowed options.")
    return value


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="to-do database location?",
    ),
) -> None:
    """Initialize the to-do database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The to-do database is {db_path}", fg=typer.colors.GREEN)


def get_todoer() -> udo.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "rptodo init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return udo.Todoer(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "rptodo init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)



@app.command()
def add(
    description: List[str] = typer.Argument(...),
    priority: int = typer.Option(2, "--priority", "-p", min=1, max=3),
    progress: int = typer.Option(0, "--progress", "-prog", min=0, max=100),
    due: str = typer.Option(2, "--due", "-d", callback=due_callback),
) -> None:
    """Add a new to-do with a DESCRIPTION."""
    todoer = get_todoer()
    todo, error = todoer.add(description, priority, progress, due)
    if error:
        typer.secho(
            f'Adding to-do failed with "{ERRORS[error]}"', fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do: "{todo['description']}" was added """
            f"""with priority: {priority}""",
            fg=typer.colors.GREEN,
        )


def spaces(number):
    return " " * number

def center(columns, text):
    side = spaces((columns-len(text)) // 2)
    return side + text + side


def visual_representation(id: int, todo: str, progress: int, columns: int) -> None:
    """
    Formats the list of tasks and outputs in the terminal.
    """

    half_index = round(columns / 2)
    main_border = "_" * (columns)
    percentage = "/" * (round((columns - half_index - 7) * progress / 100)) + str(round(progress)) + "%" 
    ID = "ID: {} ===> ".format(id) 



    main_border = typer.style(main_border, fg=typer.colors.MAGENTA)
    ID_styled = typer.style(ID, fg=typer.colors.RED)
    percentage_styled = typer.style(percentage, fg=typer.colors.BRIGHT_YELLOW)
    bar = typer.style('|', fg=typer.colors.MAGENTA)

     

    task_length = len(ID + todo)

    typer.secho(main_border)

    # if 1 line is enough to fit the task and id
    if task_length <= half_index:
        # calculate left space to feel with " " 
        left = columns - len("||" + ID + todo + spaces(half_index-task_length) + percentage)
        # design the output line
        todo_and_bar = bar + ID_styled + todo + spaces(half_index-task_length) + bar + percentage_styled + spaces(left-1) + bar
        typer.secho(todo_and_bar)

    # else split to several lines
    else:
        # split
        lines = textwrap.wrap(ID+todo, half_index, break_long_words=True)
        fragment_length = len(lines[0])
        left = columns - half_index - len(percentage) - 2
        # design the output line
        todo_and_bar = bar + lines[0].replace(ID, ID_styled) + spaces(half_index-fragment_length) + bar + percentage_styled + spaces(left-1) + bar
        typer.echo(todo_and_bar)
        # output the rest of the task body line by line
        for line in lines[1:]:
            typer.echo(line)

    typer.secho(main_border)

    return None


@app.command(name="list")
def list_all(
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="List all tasks (including completed)."
    )
) -> None:
    """List all to-dos."""
    todoer = get_todoer()
    todo_list = todoer.get_todo_list()
    if len(todo_list) == 0:
        typer.secho(
            "There are no tasks in the to-do list yet", fg=typer.colors.RED
        )
        raise typer.Exit()

    columns = os.get_terminal_size(0)[0]
    todo__sorted_list = todoer.get_sorted_todo_list(completed=all)

    typer.secho("\nTO-DO LIST:\n", fg=typer.colors.BLUE, bold=True)
    for elem in todo__sorted_list:

        if elem[1] != []:
            time_line = center(columns, elem[0].upper())
            typer.secho(time_line, fg=typer.colors.YELLOW)

            for todo in elem[1]:
                id, desc, priority, done, progress = todo.values()
                visual_representation(id, desc, progress, columns)


@app.command(name="update")
def update(
    todo_id: int = typer.Argument(...),
    priority: int = typer.Option(None, "--priority", "-p", min=1, max=3),
    done: int = typer.Option(None, "--done", "-done", min=0, max=1),
    progress: int = typer.Option(None, "--progress", "-prog", min=0, max=100),
    due: str = typer.Option(None, "--due", "-d", callback=due_callback),
) -> None:
    """Complete a to-do by setting it as done using its TODO_ID."""
    todoer = get_todoer()

    description = []
    todo, error = todoer.update(todo_id, description, priority, done, progress, due)
    if error:
        typer.secho(
            f'Updating to-do # "{todo_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do # {todo_id} "{todo['description']}" updated!""",
            fg=typer.colors.GREEN,
        )


@app.command(name="update-desc")
def update_desc(
    todo_id: int = typer.Argument(...),
    description: List[str] = typer.Argument(...)
) -> None:
    """Complete a to-do by setting it as done using its TODO_ID."""
    todoer = get_todoer()


    todo, error = todoer.update(todo_id, description)
    if error:
        typer.secho(
            f'Updating to-do # "{todo_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do # {todo_id} "{todo['description']}" updated!""",
            fg=typer.colors.GREEN,
        )


@app.command(name="complete")
def set_done(todo_id: int = typer.Argument(...)) -> None:
    """Complete a to-do by setting it as done using its TODO_ID."""
    todoer = get_todoer()
    todo, error = todoer.set_done(todo_id)
    if error:
        typer.secho(
            f'Completing to-do # "{todo_id}" failed with "{ERRORS[error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"""to-do # {todo_id} "{todo['description']}" completed!""",
            fg=typer.colors.GREEN,
        )


@app.command()
def remove(
    todo_id: int = typer.Argument(...),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove a to-do using its TODO_ID."""
    todoer = get_todoer()

    def _remove():
        todo, error = todoer.remove(todo_id)
        if error:
            typer.secho(
                f'Removing to-do # {todo_id} failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"""to-do # {todo_id}: '{todo["description"]}' was removed""",
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        todo_list = todoer.get_todo_list()
        try:
            todo = todo_list[todo_id - 1]
        except IndexError:
            typer.secho("Invalid TODO_ID", fg=typer.colors.RED)
            raise typer.Exit(1)
        delete = typer.confirm(
            f"Delete to-do # {todo_id}: {todo['description']}?"
        )
        if delete:
            _remove()
        else:
            typer.echo("Operation canceled")


@app.command(name="clear")
def remove_all(
    force: bool = typer.Option(
        ...,
        prompt="Delete all to-dos?",
        help="Force deletion without confirmation.",
    ),
) -> None:
    """Remove all to-dos."""
    todoer = get_todoer()
    if force:
        error = todoer.remove_all().error
        if error:
            typer.secho(
                f'Removing to-dos failed with "{ERRORS[error]}"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho("All to-dos were removed", fg=typer.colors.GREEN)
    else:
        typer.echo("Operation canceled")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
