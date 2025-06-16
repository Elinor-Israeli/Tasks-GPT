from client.menus import MenuChoice
from vector_store.interfaces import Addable
from backend.request.add_task_user_request import AddTaskUserRequest
from backend.request.edit_task_user_request import EditTaskUserRequest
from backend.request.view_tasks_user_request import ViewTasksUserRequest
from backend.request.mark_done_user_request import MarkDoneUserRequest
from backend.request.delete_task_user_request import DeleteTaskUserRequest

class UserRequestFactory:
    def __init__(self, task_service, user_service, genai_client, user_id, vector_store):
        self.task_service = task_service
        self.user_service = user_service
        self.genai_client = genai_client
        self.user_id = user_id
        self.vector_store = vector_store

    async def create_request(self, choice: MenuChoice, user_input):
        if choice == MenuChoice.VIEW_TASKS:
            return ViewTasksUserRequest.create(
                self.user_id,
                self.genai_client,
                user_input
            )
        elif choice == MenuChoice.ADD_TASK:
            return AddTaskUserRequest.create(
                self.user_id,
                self.genai_client,
                user_input,
                vector_store=self.vector_store
            )
        elif choice == MenuChoice.MARK_DONE:
            return MarkDoneUserRequest.create(
                self.user_id,
                self.genai_client,
                user_input
            )
        elif choice == MenuChoice.DELETE_TASK:
            return DeleteTaskUserRequest.create(
                self.user_id,
                self.genai_client,
                user_input
            )
        elif choice == MenuChoice.EDIT_TASK:
            return await EditTaskUserRequest.create(
                self.user_id,
                self.task_service,
                self.genai_client,
                user_input
            )
        else:
            return None
