
from typer.testing import CliRunner

from udo import (
    DB_READ_ERROR,
    ID_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli
)

import os

import sqlalchemy as sqla
from sqlalchemy import String, Engine, DateTime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)

from datetime import datetime

runner = CliRunner()

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
            "due": self.due
        }


class BaseTest:

    def setup_class(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        DATABASE_TEST_URI = 'sqlite:///' + os.path.join(basedir, '_todo_test.sqlite')
        engine = sqla.create_engine(DATABASE_TEST_URI)
        Base.metadata.create_all(engine)
        self.engine = engine
        self.session = Session(engine)
        self.valid_todo = ToDo({
        "description" : "Test 1",
        "priority": 3,
        "done": 0,
        "progress": 78,
        "due": datetime(2023, 5, 30)
        })

    def teardown_class(self):
        self.session.rollback()
        self.session.close()
        Base.metadata.drop_all(self.engine)