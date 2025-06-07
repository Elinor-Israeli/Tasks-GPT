from client.menu_choice import MenuChoice
from backend.request.add_task_user_request import AddTaskUserRequest
from backend.request.edit_task_user_request import EditTaskUserRequest
from backend.request.view_tasks_user_request import ViewTasksUserRequest
from backend.request.mark_done_user_request import MarkDoneUserRequest
from backend.request.delete_task_user_request import DeleteTaskUserRequest

class UserRequestFactory:
    @staticmethod
    def create_request(choice: MenuChoice, user_request, user_input):
        if choice == MenuChoice.VIEW_TASKS:
            return ViewTasksUserRequest.create(user_request)
        elif choice == MenuChoice.ADD_TASK:
            return AddTaskUserRequest.create(user_request, user_input)
        elif choice == MenuChoice.MARK_DONE:
            return MarkDoneUserRequest.create(user_request, user_input)
        elif choice == MenuChoice.DELETE_TASK:
            return DeleteTaskUserRequest.create(user_request, user_input)
        elif choice == MenuChoice.EDIT_TASK:
            return EditTaskUserRequest.create(user_request, user_input)
        else:
            return None
