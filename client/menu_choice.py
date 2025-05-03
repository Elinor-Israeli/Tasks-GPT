from enum import Enum

class MenuChoice(str, Enum):
    VIEW_TASKS = '1'
    ADD_TASK = "2"
    MARK_DONE = "3"
    DELETE_TASK = "4"
    EDIT_TASK = "5"
    NONE = "None"
