class UserRequest:
    def __init__(self, user_id, task_service, user_service, genai_client):
        self.user_id = user_id
        self.task_service = task_service
        self.user_service = user_service
        self.genai_client = genai_client
