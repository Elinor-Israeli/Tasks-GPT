# # test_todo.py
# import pytest
# from backend.models.models import Base, User, Task
# from datetime import datetime,date, timedelta
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from backend.schemas.task_schema import TaskCreate
# from datetime import date


# from backend.services.task_services import (
#     get_tasks,
#     create_task,
#     update_task,
#     delete_task,
#     get_task_by_id
# )

# @pytest.fixture
# def test_db():
#     engine = create_engine("sqlite:///:memory:")
#     Base.metadata.create_all(engine)
#     TestingSessionLocal = sessionmaker(bind=engine)
#     session = TestingSessionLocal()

#     user = User(username="elinor" , password="elinor123")
#     session.add(user)
#     session.commit()

#     due_date = datetime.strptime("2025-04-30", "%Y-%m-%d").date()

#     task = Task(title="Test task", done=False, due_date=due_date, user_id=user.id)
#     session.add(task)
#     session.commit()

#     yield session, user, task

#     session.close()

# def test_get_tasks_returns_correct_data(test_db):
#     session, user, initial_task = test_db 
#     new_task = Task(title="Test Task", done=False, due_date=date(2025, 5, 1), user_id=user.id)
#     session.add(new_task)
#     session.commit()


#     tasks = get_tasks(session, user.id)
#     assert len(tasks) >= 1
#     assert any(task.title == "Test Task" and task.user_id == user.id for task in tasks)

# def test_create_task(test_db):
#     session, user,initial_task = test_db
#     task_data = TaskCreate(title="Write pytest test", due_date = date(year=2033, month=12, day=25), done=False, user_id=user.id)
#     create_task(session, task_data)
#     task = session.query(Task).filter_by(title=task_data.title, user_id=user.id).first()

#     assert task is not None
#     assert task.title == task_data.title
#     assert task.due_date == task_data.due_date
#     assert task.done is False 

# def test_get_task_by_id_existing_task(test_db):
#     session, user, initial_task = test_db
#     task = get_task_by_id(session, initial_task.id)
#     assert task == initial_task
#     assert task.title == "Test task"

# def test_get_task_by_id_nonexistent_task(test_db):
#     session, user, initial_task = test_db
#     task = get_task_by_id(session, 999)
#     assert task is None

# def test_delete_task_existing_task(test_db):
#     session, user, initial_task = test_db
#     delete_task(session, initial_task.id)
#     deleted_task = session.query(Task).filter_by(id=initial_task.id).first()
#     assert deleted_task is None
#     session.commit() 

# def test_delete_task_nonexistent_task(test_db):
#     session, user, initial_task = test_db
#     from fastapi import HTTPException, status
#     with pytest.raises(HTTPException) as excinfo:
#         delete_task(session, 999)
#     assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

# def test_update_task_existing_task(test_db):
#     session, user, initial_task = test_db
#     updated_task = update_task(session, initial_task.id, title="Updated Task Title", done=True)
#     assert updated_task.title == "Updated Task Title"
#     assert updated_task.done == True
#     assert updated_task.due_date == initial_task.due_date
#     session.refresh(updated_task) 
#     session.commit()

# def test_update_task_partial_update(test_db):
#     session, user, initial_task = test_db
#     updated_task = update_task(session, initial_task.id, done=True)
#     assert updated_task.done == True
#     assert updated_task.title == initial_task.title #check it remains the same
#     session.refresh(updated_task) # added session.refresh
#     session.commit()
