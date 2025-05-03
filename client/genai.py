from google import genai
from typing import Optional
from menu_choice import MenuChoice
from typing import Union


class AICommandInterpreter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.prompt_template = """
You are an AI system that understands user commands in natural language.
You support the following 5 task types:

{options}

You will be given a textual command from a user.
Your job is to return the task type number (1 to 5),  
or "None" if it does not match any of the supported tasks.

Now process this command:
"{command}"
"""
        self.prompt_template_view_task = """
You are an AI system that understands user commands in natural language. the user chose to view his tasks , now you need to understand what kind of task type he wants to view:

{view_options}
Your job is to return the task type number (1 to 5)
or "None" if it does not match any of the supported tasks.
Now process this command:
"{command}"
        """ 
        self.prompt_template_edit_task = """
You are an AI system that understands user commands in natural language. the user chose to edit his tasks , now you need to understand what he wants to edit:

{edit_options}
Your job is to return the task type number (1 to 4)
or "None" if it does not match any of the supported tasks.
Now process this command:
"{command}"
        """ 

    def interpret_command(self, user_input: str, options: str) -> MenuChoice:
        prompt = self.prompt_template.format(command=user_input, options=options)
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        result = response.text.strip()
        return MenuChoice(result)

    def interpret_view_task_command(self, user_input: str, view_options: str) -> Union[str, None]:
        prompt = self.prompt_template_view_task.format(command=user_input, view_options=view_options)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        result = response.text.strip().lower()

        return result

    def interpret_edit_task_command(self, user_input: str, edit_options: str) -> Union[str, None]:
        prompt = self.prompt_template_edit_task.format(command=user_input,edit_options=edit_options)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        result = response.text.strip().lower()

        return result        