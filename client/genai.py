from google import genai
from typing import Optional
from menu_choice import MenuChoice

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

    def interpret_command(self, user_input: str, options: str) -> MenuChoice:
        prompt = self.prompt_template.format(command=user_input, options=options)
        print(f"prompt:{prompt}")
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        result = response.text.strip()
        return MenuChoice(result)
       