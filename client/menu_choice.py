from enum import Enum

class MenuChoice(str, Enum):
    VIEW_TASKS = '1'
    ADD_TASK = "2"
    MARK_DONE = "3"
    DELETE_TASK = "4"
    VIEW_COMPLETED = "5"
    VIEW_INCOMPLETE = "6"
    EDIT_TASK = "7"
    VIEW_UPCOMING = "8"
    VIEW_OVERDUE = "9"
    EXIT = "10"
