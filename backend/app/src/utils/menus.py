from enum import Enum

class MenuChoice(str, Enum):
    VIEW_TASKS = "1"
    ADD_TASK = "2"
    MARK_DONE = "3"
    DELETE_TASK = "4"
    EDIT_TASK = "5"
    NONE = "None"

view_options = """
    1. Completed Tasks
    2. Incomplete Tasks
    3. Overdue Tasks
    4. Upcoming Tasks
    5. All Tasks
    """    

class ViewOption(str, Enum):
    COMPLETED_TASKS = '1'
    INCOMPLETE_TASKS = '2'
    OVERDUE_TASKS = '3'
    UPCOMING_TASKS ='4'
    ALL_TASKS = '5'