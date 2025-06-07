from google import genai
from typing import Optional, Union
from client.menu_choice import MenuChoice
import json
from datetime import date
import time

class AICommandInterpreter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

        self.prompt_template = """
You are an AI system that understands user commands in natural language.
You support the following options:

{options}

You will be given a textual command from a user.
Your job is to return the option number (1 to N),  
or "None" if it does not match any of the supported options.

Now process this command:
"{command}"
"""

        self.prompt_template_view_task = """
You are an AI system that understands user commands in natural language. The user chose to view his tasks. Now you need to understand what kind of task type he wants to view:

{view_options}

Your job is to return the task type number (1 to 5), or "None" if it does not match any of the supported tasks.

Now process this command:
"{command}"
""" 

        self.prompt_template_edit_task = """
You are an AI system that understands user commands in natural language. The user chose to edit his tasks. Now you need to understand what he wants to edit:

{edit_options}

Your job is to return the task type number (1 to 4), or "None" if it does not match any of the supported tasks.

Now process this command:
"{command}"
""" 

    def interpret_command(self, user_input: str, options: Optional[str] = None) -> MenuChoice:
        if options:
            prompt = self.prompt_template.format(command=user_input, options=options)
        else:
            prompt = """
You are an AI system that understands user commands in natural language.
You support the following 5 task types:

1. Extraction - extract task name and date from the sentence → return JSON: {"name": .., "date": ..}
2. Search - embeddings search
3. Planning
4. Most urgent
5. Break down big task into smaller tasks

You will be given a textual command from a user.
Your job is to return the task type number (1 to 5),  
or "None" if it does not match any of the supported tasks.

Now process this command:
"{command}"
""".format(command=user_input)

        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )
                result = response.text.strip()
                print(f"[DEBUG] interpret_command result: {result}")

                try:
                    return MenuChoice(result)
                except ValueError:
                    return MenuChoice.NONE

            except Exception as e:
                print(f"[ERROR] Gemini API call failed (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Returning NONE.")
                    return MenuChoice.NONE

    def interpret_view_task_command(self, user_input: str, view_options: str) -> Union[str, None]:
        prompt = self.prompt_template_view_task.format(command=user_input, view_options=view_options)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip().lower()
            print(f"[DEBUG] interpret_view_task_command result: {result}")
            return result

        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return None

    def interpret_edit_task_command(self, user_input: str, edit_options: str) -> Union[str, None]:
        prompt = self.prompt_template_edit_task.format(command=user_input, edit_options=edit_options)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip().lower()
            print(f"[DEBUG] interpret_edit_task_command result: {result}")
            return result

        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return None

    def extract_task_data(self, user_input: str) -> dict:
        today_str = date.today().strftime("%Y-%m-%d")

        extraction_prompt = f"""
Today is {today_str}.

You are an expert AI assistant that extracts structured data from text.

Your job is to extract two things:
1. Task name
2. Task due date

You MUST return a VALID JSON in this exact format:

{{
    "name": "task name here",
    "date": "YYYY-MM-DD"  // If a date is mentioned. If no date → "None".
}}

IMPORTANT:
- Understand dates in ANY FORMAT:
    * "2025/06/05"
    * "06/05/2025"
    * "next Monday"
    * "tomorrow"
    * "in two weeks"
    * "on July 1st"
    * "this Friday"
    * "next week"
    * "next month"
- Normalize ALL dates to "YYYY-MM-DD" using the current date (Today is {today_str}).
- If no date is mentioned → set "date" to "None".

Here is the sentence:

"{user_input}"

Now return ONLY the JSON:
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[extraction_prompt]
            )
            result = response.text.strip()

            print(f"[DEBUG] extract_task_data raw result: {result}")

            try:
                extracted_data = json.loads(result)
            except Exception:
                extracted_data = {"name": None, "date": None}

            print(f"[DEBUG] extract_task_data parsed: {extracted_data}")

            return extracted_data

        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            return {"name": None, "date": None}
