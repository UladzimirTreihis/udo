"""This module provides the RP UDo database functionality."""

import configparser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional
import os

import logging

import sqlalchemy as sqla
from sqlalchemy import String, Engine, DateTime
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)

from udo import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

from udo.due_options import ToDoDate

DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "Desktop/codes/todo_project/_todo.sqlite"
)

#SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath(DEFAULT_DB_FILE_PATH)

class Base(DeclarativeBase):
    pass

class ToDo(Base):
    __tablename__ = "todo"
    extend_existing = True
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(240))
    priority: Mapped[int] = mapped_column(default=2)
    done: Mapped[int] = mapped_column(default=0)
    progress: Mapped[int] = mapped_column(default=0)
    due: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    def __init__(self, d=None) -> None:
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)
    def __repr__(self) -> str:
        return f"ToDo(id={self.id!r}, description={self.description!r}, priority={self.priority!r}, done={self.done!r}"
    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "done": self.done,
            "progress": self.progress,
        }

def get_database_path(config_file: Path) -> Path:
    """Return the current path to the to-do database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


def get_db_uri(config_file: Path) -> str:
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return config_parser["General"]["uri"]


def get_engine(config_file: Path) -> Engine:
    db_uri = get_db_uri(config_file)
    return sqla.create_engine(db_uri)


def get_session(config_file: Path) -> Session:
    #db_uri = get_db_uri(config_file)
    db_uri = "sqlite:///" + os.path.abspath(DEFAULT_DB_FILE_PATH)
    engine = sqla.create_engine(db_uri)
    return Session(engine)


def get_session_by_uri(db_uri: str) -> Session:
    engine = sqla.create_engine(db_uri)
    return Session(engine)

def init_database(db_path: Path) -> int:
    """Create the to-do database."""
    try:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath(db_path)
        engine = sqla.create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(bind=engine)
        with Session(engine) as session:
            dummy_todo = ToDo({
                "description": "Dummy ToDo",
                "due": datetime(2023, 12, 31)
            })
            session.add(dummy_todo)
            session.commit()
        return SUCCESS
    except OperationalError:
        return DB_WRITE_ERROR


class DBResponse(NamedTuple):
    todo_list: List[Dict[str, Any]]
    error: int

class DBObjectResponse(NamedTuple):
    todo: ToDo
    error: int

class DBFiteredResponse():
    def __init__(self, query, error):
        if query != None:
            filtered = [
                
                ("this year", todos_listed(query, relativedelta(years=1), relativedelta(months=1))),
                ("january", todos_listed_month(query, ToDoDate().due_month(1), ToDoDate().due_month(12))),
                ("february", todos_listed_month(query, ToDoDate().due_month(2), ToDoDate().due_month(1))),
                ("march", todos_listed_month(query, ToDoDate().due_month(3), ToDoDate().due_month(2))),
                ("april", todos_listed_month(query, ToDoDate().due_month(4), ToDoDate().due_month(3))),
                ("may", todos_listed_month(query, ToDoDate().due_month(5), ToDoDate().due_month(4))),
                ("june", todos_listed_month(query, ToDoDate().due_month(6), ToDoDate().due_month(5))),
                ("july", todos_listed_month(query, ToDoDate().due_month(7), ToDoDate().due_month(6))),
                ("august", todos_listed_month(query, ToDoDate().due_month(8), ToDoDate().due_month(7))),
                ("september", todos_listed_month(query, ToDoDate().due_month(9), ToDoDate().due_month(8))),
                ("october", todos_listed_month(query, ToDoDate().due_month(10), ToDoDate().due_month(9))),
                ("november", todos_listed_month(query, ToDoDate().due_month(11), ToDoDate().due_month(10))),
                ("december", todos_listed_month(query, ToDoDate().due_month(12), ToDoDate().due_month(11))),

                ("this month", todos_listed(query, relativedelta(months=1), relativedelta(days=7))),
                ("this week", todos_listed(query, relativedelta(days=7), relativedelta(days=2))),
                ("tomorrow", todos_listed(query, relativedelta(days=2), relativedelta(days=1))),
                ("today", todos_listed(query, relativedelta(days=1), relativedelta(days=0))),
                ("outdated", todos_listed(query, relativedelta(days=0), -relativedelta(years=5))),
            ]

            self.todo_list: List[tuple[str, List[Dict[str, Any]]]] = filtered
        else:
            self.todo_list = []
        self.error: int = error


def todos_listed(query: Session, delta_up: relativedelta, delta_down: relativedelta) -> List[dict]:
    filtered = query.where((ToDo.due < datetime.now() + delta_up) & (ToDo.due > datetime.now() + delta_down)).all()
    array = []
    for todo in filtered:
        if todo != None:
            array.append(todo.as_dict())
        else:
            array.append(None)
    return array

def todos_listed_month(query: Session, month_up: datetime, month_down: datetime) -> List[dict]:
    filtered = query.where((ToDo.due <= month_up) & (ToDo.due > month_down)).all()
    array = []
    for todo in filtered:
        if todo != None:
            array.append(todo.as_dict())
        else:
            array.append(None)
    return array


class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_todos(self) -> DBResponse:
        with self._db_path as path:
            session = get_session(path)
            try:
                return DBResponse(
                    [todo.as_dict() for todo in session.query(ToDo).all()],
                    SUCCESS
                )
            except:
                return DBResponse([], DB_READ_ERROR)

    def read_and_sort_todos(self, completed: bool) -> List[tuple[str, List[Dict[str, Any]]]]:
        with self._db_path as path:
            session = get_session(path)
            if completed:
                query = session.query(ToDo)
            else:
                query = session.query(ToDo).where(ToDo.done==0)
            try:
                return DBFiteredResponse(query, SUCCESS)
            except:
                return DBFiteredResponse(None, DB_READ_ERROR)

    def write_todos(self, todo_list: List[Dict[str, Any]]) -> DBResponse:
        try:
            with self._db_path as path:
                session = get_session(path)
                session.add_all(
                    [ToDo(d) for d in todo_list]
                )
                try:
                    session.commit()
                except:
                    logging.exception("An exception below:")

            return DBResponse(todo_list, SUCCESS)
        except: 
            return DBResponse(todo_list, DB_WRITE_ERROR)

    def get_todo(self, todo_id):
        try:
            with self._db_path as path:
                session = get_session(path)
                todo = session.query(ToDo).where(ToDo.id == todo_id).scalar() 
                return DBObjectResponse(todo, SUCCESS)
        except:
            return DBObjectResponse(None, DB_READ_ERROR)

    def delete_todo(self, todo_id):
        try:
            with self._db_path as path:
                session = get_session(path)
                todo = session.query(ToDo).where(ToDo.id == todo_id).scalar() 
                todo_dict = todo.as_dict()
                session.delete(todo)
                try:
                    session.commit()
                    return DBObjectResponse(todo_dict, SUCCESS)
                except:
                    session.rollback()
                    return DBObjectResponse(todo_dict, DB_WRITE_ERROR)
            
        except:
            return DBObjectResponse(None, DB_WRITE_ERROR)

    def delete_all(self):
        try:
            with self._db_path as path:
                session = get_session(path)
                session.query(ToDo).delete()
                try:
                    session.commit()
                    return DBObjectResponse({}, SUCCESS)
                except:
                    session.rollback()
                    return DBObjectResponse({}, DB_WRITE_ERROR)
        except:
            return DBObjectResponse(None, DB_WRITE_ERROR)

    def update_todo(self, todo_id, **kwargs):
        try:
            with self._db_path as path:
                session = get_session(path)
                todo = session.query(ToDo).where(ToDo.id == todo_id)
                print(kwargs)

                todo.update(kwargs)
                
                try:
                    session.commit()
                    return DBObjectResponse(todo.scalar().as_dict(), SUCCESS)
                except:
                    session.rollback()
                    return DBObjectResponse({}, DB_WRITE_ERROR)
            
        except:
            return DBObjectResponse(None, DB_WRITE_ERROR)