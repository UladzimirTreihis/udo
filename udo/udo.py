"""This module provides the RP UDo model-controller."""

from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from udo import DB_READ_ERROR, ID_ERROR
from udo.database import DatabaseHandler

from udo.due_options import sort_due


class CurrentTodo(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(
        self,
        description: List[str],
        priority: int = 2,
        progress: int = 0,
        due: str = 'today'
        ) -> CurrentTodo:
        """Add a new to-do to the database."""
        description_text = " ".join(description)
        if not description_text.endswith("."):
            description_text += "."

        sorted_due = sort_due(due)

        todo = {
            "description": description_text,
            "priority": priority,
            "done": 0,
            "progress": progress,
            "due": sorted_due
        }
        write = self._db_handler.write_todos([todo])
        return CurrentTodo(todo, write.error)

    def get_todo_list(self) -> List[Dict[str, Any]]:
        """Return the current to-do list."""
        read = self._db_handler.read_todos()
        return read.todo_list

    def get_sorted_todo_list(self, completed: bool) -> List[tuple[str, List[Dict[str, Any]]]]:
        """Return the current SORTED to-do list."""
        read = self._db_handler.read_and_sort_todos(completed)
        return read.todo_list

    def set_done(self, todo_id: int) -> CurrentTodo:
        """Set a to-do as done."""
        response = self._db_handler.update_todo(todo_id, done=1, progress=100)

        return CurrentTodo(response.todo, response.error)

    def update(self, 
        todo_id: int,
        description: List[str] = [],
        priority: int = None,
        done: int = None,
        progress: int = None,
        due: str = None
        ) -> CurrentTodo:
        """Update a to-do."""

        print('description = ', description)
        if description != []:
            description_text = " ".join(description)
        else:
            description_text = None

        sorted_due = sort_due(due)

        todo = {
            "description": description_text,
            "priority": priority,
            "done": done,
            "progress": progress,
            "due": sorted_due
        }
        kwargs = {}
        for key, value in todo.items():
            if value != None:
                kwargs[key] = value
        response = self._db_handler.update_todo(todo_id, **kwargs)

        return CurrentTodo(response.todo, response.error)

    def remove(self, todo_id: int) -> CurrentTodo:
        """Remove a to-do from the database using its id or index."""
        response = self._db_handler.delete_todo(todo_id)

        return CurrentTodo(response.todo, response.error)

    def remove_all(self) -> CurrentTodo:
        """Remove all to-dos from the database."""
        response = self._db_handler.delete_all()
        return CurrentTodo({}, response.error)
