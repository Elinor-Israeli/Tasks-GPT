from google import genai
# import google.generativeai as genai
from typing import Optional, Union
from src.utils.menus import MenuChoice
import json
from datetime import date
import time
import re
from src.utils.logger import logger

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

    def interpret_command(self, user_input: str, options: Optional[str]) -> MenuChoice:
        prompt = self.prompt_template.format(command=user_input, options=options)
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )
                result = response.text.strip()
                logger.debug(f"interpret_command result: {result}")

                try:
                    return MenuChoice(result)
                except ValueError:
                    return MenuChoice.NONE

            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        logger.info("Max retries reached. Returning NONE.")
        return MenuChoice.NONE

    def interpret_view_task_command(self, user_input: str, view_options: str) -> Union[str, None]:
        prompt = self.prompt_template_view_task.format(command=user_input, view_options=view_options)
    
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip().lower()
            logger.debug(f"interpret_view_task_command result: {result}")
            return result

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    def interpret_edit_task_command(self, user_input: str, edit_options: str) -> Union[str, None]:
        prompt = self.prompt_template_edit_task.format(command=user_input, edit_options=edit_options)
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip().lower()
            logger.debug(f"interpret_edit_task_command result: {result}")
            return result
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
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
- Please note that vague tasks like "add a task" or "create a task" are not titles. Only consider real task descriptions as titles. If not, return "None" as title 
Here is the sentence:
"{user_input}"
Now return ONLY the JSON
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[extraction_prompt]
            )
            result = response.text.strip()

            logger.debug(f"extract_task_data raw result: {result}")

            result_clean = re.sub(r"```json|```", "", result.strip()).strip()

            try:
                extracted_data = json.loads(result_clean)
            except Exception as e:
                logger.debug(f"JSON parse failed: {e}")
                extracted_data = {"name": None, "date": None}

            logger.debug(f"extract_task_data parsed: {extracted_data}")

            return extracted_data

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {"name": None, "date": None}

    def extract_edit_task_data(self, user_input: str) -> dict:
        today_str = date.today().strftime("%Y-%m-%d")
        prompt = f"""
Today is {today_str}.

You are an expert AI assistant that helps update tasks. The user gave you a sentence describing what they want to change about a task.

Extract the following from the sentence:
- New task title (if they want to change it)
- New due date (if they want to change it)

Return this JSON format exactly:
{{
    "title": "new title here or null",
    "due_date": "YYYY-MM-DD or null"
}}

If the user does not want to change a field, return null for it.

Now process this sentence:
"{user_input}"

Return ONLY the JSON.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip()

            result_clean = re.sub(r"^```json\s*|```$", "", result.strip(), flags=re.MULTILINE)
            return json.loads(result_clean)
        except Exception as e:
            logger.error(f"Failed to extract edit task data: {e}")
            return {"title": None, "due_date": None}

    def extract_task_id_or_title(self, user_input: str) -> dict:
        prompt = f"""
    You are an expert AI assistant. The user wants to select a task to mark as done.
    Extract EITHER the TASK ID (number) OR the TASK TITLE (string) from this command:
    "{user_input}"
    Return a VALID JSON in this exact format:

    {{
        "task_id": 123,      // If the user said a task ID. If no ID, set to null.
        "task_title": "..."  // If the user said a title. If no title, set to null.
    }}

    IMPORTANT:
    - If both are mentioned, return both.
    - If neither is mentioned, set both to null.
    Now return ONLY the JSON.
    """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip()
            logger.debug(f"extract_task_id_or_title raw result: {result}")
            result_clean = re.sub(r"^```json\s*|```$", "", result.strip(), flags=re.MULTILINE)
            try:
                parsed = json.loads(result_clean)
            except Exception as e:
                logger.debug(f"JSON parse failed: {e}")
                parsed = {"task_id": None, "task_title": None}
            logger.debug(f"extract_task_id_or_title parsed: {parsed}")
            return parsed

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {"task_id": None, "task_title": None}

    def extract_task_id_or_title_to_edit(self, user_input: str) -> dict:
        today_str = date.today().strftime("%Y-%m-%d")
        prompt = f"""
    You are an expert AI assistant. The user wants to select a task to edit.
    Extract EITHER the TASK ID (number) OR the TASK TITLE (string) from this command:
    "{user_input}"
    Return a VALID JSON in this exact format:

    {{
        "task_id": 123,      // If the user said a task ID. If no ID, set to null.
        "task_title": "..."  // If the user said a title. If no title, set to null.
    }}

    IMPORTANT:
    - If both are mentioned, return both.
    - If neither is mentioned, set both to null.
    - Please note that vague tasks like "edit a task" or "edit a title" or "change a due date" or "change the title" are not titles. Only consider real task descriptions as titles. If not, return "None" as title.

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
    Now return ONLY the JSON.
    """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result = response.text.strip()
            logger.debug(f"extract_task_id_or_title raw result: {result}")
            result_clean = re.sub(r"^```json\s*|```$", "", result.strip(), flags=re.MULTILINE)
            try:
                parsed = json.loads(result_clean)
            except Exception as e:
                logger.debug(f"JSON parse failed: {e}")
                parsed = {"task_id": None, "task_title": None}
            logger.debug(f"extract_task_id_or_title parsed: {parsed}")
            return parsed
        
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return {"task_id": None, "task_title": None}
