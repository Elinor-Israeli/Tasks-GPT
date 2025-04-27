# test_todo.py
import pytest
from models import create_engine
from models import sessionmaker
from datetime import datetime,date, timedelta

from models import Base, User, Task  
from todo_app import (
    get_tasks, view_tasks, add_task, edit_task, mark_done,
    view_complete_tasks, view_incomplete_tasks, view_upcoming_tasks,
    view_overdue_tasks
)

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    user = User(username="elinor")
    session.add(user)
    session.commit()

    due_date = datetime.strptime("2025-04-30", "%Y-%m-%d").date()

    task = Task(title="Test task", done=False, due_date=due_date, user_id=user.id)
    session.add(task)
    session.commit()

    yield session, user

    session.close()

def test_get_tasks_returns_correct_data(test_db):
    session, user = test_db 
    new_task = Task(title="Test Task", done=False, due_date=date(2025, 5, 1), user_id=user.id)
    session.add(new_task)
    session.commit()


    tasks = get_tasks(session, user.id)
    assert len(tasks) >= 1
    assert any(task.title == "Test Task" and task.user_id == user.id for task in tasks)

def test_view_tasks(capsys, test_db):
    session, user = test_db
    view_tasks(session, user.id)
    captured = capsys.readouterr() # instead of print
    assert "Test task" in captured.out
    assert "❌" in captured.out
    assert "Due: 2025-04-30" in captured.out

def test_add_task(test_db):
    session, user = test_db
    title = "Write pytest test"
    due_date = "2025-04-30"
    add_task(session, title, due_date, user)
    task = session.query(Task).filter_by(title=title, user_id=user.id).first()

    assert task is not None
    assert task.title == title
    assert task.due_date.isoformat() == due_date
    assert task.done is False 

def test_edit_task_title(test_db, capsys):
    session, user = test_db
    task = Task(title='Old Test', due_date=date(2025, 5, 1), user_id=user.id)  
    session.add(task)  
    session.commit()

    edit_task(session, user.id, task.id, choice="1", new_title="New Title")

    updated_task = session.query(Task).filter_by(id=task.id, user_id=user.id).first()
    assert updated_task.title == "New Title"

    captured = capsys.readouterr()
    assert "Title updated!" in captured.out

def test_edit_task_due_date(test_db, capsys):
    session, user = test_db
    task = Task(title='Some Task',due_date=date(2025, 5, 1),user_id=user.id)
    session.add(task)
    session.commit()

    edit_task(session, user.id, task.id, choice='2', new_due_date=date(2025, 6, 1))

    updated_task = session.query(Task).filter_by(id=task.id, user_id=user.id).first()
    assert updated_task.due_date == date(2025, 6, 1)

    out = capsys.readouterr().out
    assert "Due date updated!" in out

def test_edit_task_title_and_due_date(test_db, capsys):
    session, user = test_db
    task = Task(title='Initial Test', due_date=date(2025, 4, 1), user_id=user.id)
    session.add(task)
    session.commit()

    edit_task(session, user.id, task.id, choice="3", new_title="Updated Title", new_due_date=date(2025, 4, 1))
    updated_task = session.query(Task).filter_by(id=task.id, user_id=user.id).first()
   
    assert updated_task.title == "Updated Title"
    assert updated_task.due_date == date(2025, 4, 1)

    out = capsys.readouterr().out
    assert "Task updated!" in out

def test_mark_done(test_db, capsys):
    session, user = test_db
    task = Task(title='Test Task', due_date=date(2025, 4, 21), user_id=user.id)
    session.add(task)
    session.commit()

    mark_done(session, user.id, task.id)
    marked_task = session.query(Task).filter_by(id=task.id, user_id=user.id).first()
    assert marked_task.done is True

    captured = capsys.readouterr()
    assert "Task marked as done" in captured.out

def test_view_complete_tasks(capsys, test_db):
    session, user = test_db
    completed_task = Task(title="Completed Task", due_date=date(2025, 4, 20), done=True, user_id=user.id)
    incomplete_task = Task(title="Incomplete Task", due_date=date(2025, 4, 22), done=False, user_id=user.id)
    session.add_all([completed_task, incomplete_task])
    session.commit()

    view_complete_tasks(session, user.id)
    captured = capsys.readouterr()

    assert "Completed Task ✅" in captured.out
    assert "Incomplete Task" not in captured.out

def test_view_incomplete_tasks(capsys, test_db):
    session, user = test_db
    completed_task = Task(title="Completed Task", due_date=date(2025, 4, 20), done=True, user_id=user.id)
    incomplete_task = Task(title="Incomplete Task", due_date=date(2025, 4, 22), done=False, user_id=user.id)
    session.add_all([completed_task, incomplete_task])
    session.commit()

    view_incomplete_tasks(session, user.id)
    captured = capsys.readouterr()

    assert "Incomplete Task" in captured.out
    assert "❌" in captured.out

def test_view_upcoming_tasks(capsys, test_db):
    session, user = test_db
    future_date = (date.today() + timedelta(days=3))

    task = Task(title='Future Task', due_date=future_date, done=False, user_id=user.id )
    session.add(task)
    session.commit()

    view_upcoming_tasks(session, user.id)
    captured = capsys.readouterr()
    print(captured.out)

    assert "--- Upcoming Tasks ---" in captured.out
    assert "Future Task" in captured.out
   
def test_view_overdue_tasks(capsys, test_db):
    session, user = test_db
    past_date = (date.today() - timedelta(days=3))

    task = Task(title='Overdue Task', due_date=past_date, done=False, user_id=user.id)
    session.add(task)
    session.commit()

    view_overdue_tasks(session, user.id)
    captured = capsys.readouterr()

    assert "--- Overdue Tasks ---" in captured.out or "--- overdue Tasks ---" in captured.out
    assert "Overdue Task" in captured.out
    assert "⚠️" in captured.out    