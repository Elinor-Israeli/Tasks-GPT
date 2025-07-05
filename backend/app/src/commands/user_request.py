from typing import Protocol

class UserRequest:
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
