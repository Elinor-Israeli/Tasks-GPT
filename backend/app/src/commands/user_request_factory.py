from src.commands.add_task_user_request import AddTaskUserRequest
from src.commands.delete_task_user_request import DeleteTaskUserRequest
from src.commands.edit_task_user_request import EditTaskUserRequest
from src.commands.mark_done_user_request import MarkDoneUserRequest
from src.commands.view_tasks_user_request import ViewTasksUserRequest
from src.genai import AICommandInterpreter 
from src.http_services.task_http_service import TaskHttpService
from src.http_services.user_http_service import UserHttpService
from src.vector_store.interfaces import SearchableVectorStore
from src.utils.menus import MenuChoice
from src.utils.logger import logger  

class UserRequestFactory:
    def __init__(
        self, 
        task_service: TaskHttpService, 
        user_service: UserHttpService, 
        genai_client:AICommandInterpreter, 
        user_id: int, 
        vector_store:SearchableVectorStore,
    ):
        self.task_service = task_service
        self.user_service = user_service
        self.genai_client = genai_client
        self.user_id = user_id
        self.vector_store = vector_store

    async def create_request(self, choice: MenuChoice, user_input, communicator):
        if choice == MenuChoice.VIEW_TASKS:
            return await ViewTasksUserRequest.create(
                user_id=self.user_id,
                genai_client=self.genai_client,
                user_input=user_input,
                vector_searcher=self.vector_store,
                communicator=communicator
            )
        elif choice == MenuChoice.ADD_TASK:
            logger.info("Add task is called")
            return await AddTaskUserRequest.create(
                user_id=self.user_id,
                genai_client=self.genai_client,
                user_input=user_input,
                communicator=communicator          
            )
        elif choice == MenuChoice.MARK_DONE:
            return await MarkDoneUserRequest.create(
                user_id=self.user_id,
                genai_client=self.genai_client,
                user_input=user_input,
                vector_searcher=self.vector_store,
                communicator=communicator

            )
        elif choice == MenuChoice.DELETE_TASK:
            return await DeleteTaskUserRequest.create(
                user_id=self.user_id,
                genai_client=self.genai_client,
                user_input=user_input,
                vector_searcher=self.vector_store,
                communicator=communicator

            )
        elif choice == MenuChoice.EDIT_TASK:
            return await EditTaskUserRequest.create(
                user_id=self.user_id,
                task_service=self.task_service,
                genai_client=self.genai_client,
                user_input=user_input,
                vector_searcher=self.vector_store,
                communicator=communicator
            )
        else:
            return None
