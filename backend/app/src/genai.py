from google import genai
from typing import Optional, Union
from src.utils.menus import MenuChoice
import json
import time
import re
from datetime import date
from src.utils.logger import logger
from src.utils.prompt_templates import (
    INTERPRET_COMMAND_TEMPLATE,
    VIEW_TASK_TEMPLATE,
    EXTRACT_TASK_TEMPLATE,
    EXTRACT_EDIT_TASK_TEMPLATE,
    EXTRACT_ID_OR_TITLE_TEMPLATE,
    EXTRACT_ID_OR_TITLE_TO_EDIT_TEMPLATE,
    MENU_TEMPLATE,
    CONFIRMATION_TEMPLATE
)

class AICommandInterpreter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _call_gemini(self, prompt: str, retries: int = 3) -> Optional[str]:
        logger.info(f"prompt: {prompt}")
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(model=self.model, contents=[prompt])
                logger.info(f"response: {response}")
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        logger.warning("Max retries reached.")
        return None

    def _safe_json_parse(self, text: str, fallback: dict) -> dict:
        try:
            clean = re.sub(r"^```json\s*|```$", "", text.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean)
            if isinstance(parsed, dict):
                logger.info(f"Parsed json returned: {parsed}")
                return parsed
            elif isinstance(parsed, str):
                logger.warning(f"Parsed string instead of dict: {parsed}")
                return fallback
            else:
                logger.error(f"Unexpected type: {type(parsed)} | content: {parsed}")
                return fallback
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error: {e} | raw response: {text}")
            return fallback
        except Exception as e:
            logger.error(f"Unexpected error in _safe_json_parse: {e} | raw response: {text}")
            return fallback

    # --- INTERPRETERS ---

    def interpret_command(self, user_input: str, options: Optional[str]) -> MenuChoice:
        prompt = INTERPRET_COMMAND_TEMPLATE.format(command=user_input, options=options)
        logger.info(f'IC prompt - {prompt}')
        result = self._call_gemini(prompt)
        logger.info(f'IC result - {result}')
        try:
            return MenuChoice(result)
        except Exception:
            return MenuChoice.NONE

    def interpret_view_task_command(self, user_input: str, view_options: str) -> dict:
        prompt = VIEW_TASK_TEMPLATE.format(command=user_input, view_options=view_options)
        logger.info(f"VC prompt - {prompt}")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt]
            )
            result_raw = response.text.strip()

            logger.info(f"interpret_view_task_command raw: {result_raw}")


            cleaned = re.sub(r"^```json\s*|```$", "", result_raw.strip(), flags=re.MULTILINE)
            logger.info(f'json : {cleaned}')
            try:
                result = json.loads(cleaned)
                return result 
            except json.JSONDecodeError as e:
                logger.error(f'JSON parsing failed: {e}')
                logger.info(f'Cleaned AI output (before parsing): {repr:cleaned}')
                return {
                "status": "error",
                "message": "The AI response could not be parsed as JSON.",
                "choice": None
            }

        except Exception as e:
            logger.error(f"Gemini AI failed to parse view task command: {e}")
            return {"status": "error", "message": "Something went wrong.", "choice": None}

    # --- EXTRACTION ---

    def extract_task_data(self, user_input: str) -> dict:
        prompt = EXTRACT_TASK_TEMPLATE.format(user_input=user_input, today=date.today())
        logger.info(f"prompt: {prompt}")
        result = self._call_gemini(prompt)
        return self._safe_json_parse(result or '', {"name": None, "date": None})

    def extract_edit_task_data(self, user_input: str) -> dict:
        prompt = EXTRACT_EDIT_TASK_TEMPLATE.format(user_input=user_input, today=date.today())
        result = self._call_gemini(prompt)
        return self._safe_json_parse(result or '', {"title": None, "due_date": None})

    def extract_task_id_or_title(self, user_input: str) -> dict:
        prompt = EXTRACT_ID_OR_TITLE_TEMPLATE.format(user_input=user_input)
        result = self._call_gemini(prompt)
        return self._safe_json_parse(result or '', {"task_id": None, "task_title": None})

    def extract_task_id_or_title_to_edit(self, user_input: str) -> dict:
        prompt = EXTRACT_ID_OR_TITLE_TO_EDIT_TEMPLATE.format(user_input=user_input, today=date.today())
        result = self._call_gemini(prompt)
        return self._safe_json_parse(result or '', {"task_id": None, "task_title": None})

    # --- UI GENERATION ---

    def generate_conversational_menu(self, username: Optional[str] = None) -> str:
        prompt = MENU_TEMPLATE.format(name_intro=f"{username}," if username else "there")
        return self._call_gemini(prompt) or "Hi! 😊 What would you like to do?"

    def generate_conversational_response(self, user_input: str, intent: MenuChoice, include_guide: bool = False) -> str:
        prompt = CONFIRMATION_TEMPLATE.format(user_input=user_input, intent=intent.name)
        logger.info(f'GC prompt- {prompt}')
        confirmation = self._call_gemini(prompt) or f"Okay! Let’s handle that '{intent.name.lower()}' request ✅"
        logger.info(f'GC confirmation- {confirmation}')
        return confirmation
