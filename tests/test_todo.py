from typer.testing import CliRunner

from udo import (
    DB_READ_ERROR,
    ID_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli
)

from datetime import datetime

runner = CliRunner()

from tests.setup import BaseTest, ToDo

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


class TestToDo(BaseTest):

    def test_ToDo(self):
        todo1 = ToDo(
            {"description" : "Todo1", "due": datetime.now()}
            )
        todo2 = ToDo(
            {"description" : "Todo1", "priority": 3, "done": 1, "due": datetime.now()}
            )
        self.session.add(todo1)
        self.session.commit()
        self.session.add(todo2)
        self.session.commit()
        assert todo1.id < todo2.id
        assert todo1.due < todo2.due
        assert todo1.priority == 2
        assert todo2.priority == 3

    def test_as_dict(self):
        todo = self.session.query(ToDo).first()
        todo_dict = todo.as_dict()
        assert type(todo_dict) == dict
        assert type(todo_dict["priority"]) == int
        assert type(todo_dict["due"]) == datetime



