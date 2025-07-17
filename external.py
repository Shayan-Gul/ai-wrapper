from mistralai import Mistral
from google import genai
from google.genai import types
from dotenv import dotenv_values
from random import choice
import sqlite3
import os
from typing import Self, Any
import sys

class Api_Manager:

    @staticmethod
    def _initilise_api_keys_from_db(keys: dict[str, str]) -> tuple[str, str, bool]:
        with Database("main.db") as db:
            db.create_table("gemini_keys", {"id": "INT PRIMARY KEY", "key": "TEXT NOT NULL", "validity": "INTEGER", "Reset_Validity_Of_Key": "INTEGER NOT NULL"})
            all_keys = [(i+1, api_key, True, 0) for i, api_key in enumerate(keys.values())]
            db.insert_batch_data("gemini_keys", tuple(all_keys))

    @staticmethod
    def get_valid_keys_from_db() -> str | None:
        with Database("main.db") as db:
            db.con.row_factory = sqlite3.Row 
            db.cur = db.con.cursor()
            db.cur.execute("SELECT key FROM gemini_keys WHERE validity")
            valid_random_key_entry = db.cur.fetchone()
            valid_random_key = valid_random_key_entry["key"]
            if valid_random_key: return valid_random_key

    def __init__(self, path_to_env: str):
        self._initilise_api_keys_from_db(dotenv_values(path_to_env))

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name if db_name.endswith(".db") else f"{db_name}.db"
        self.con = None
        self.cur = None

    def __enter__(self) -> Self:
            self.con = sqlite3.connect(self.db_name)
            self.cur = self.con.cursor()
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.con:
            self.con.commit()
            if self.cur:    
                self.cur.close()
            self.con.close()
        
    def create_table(self, table_name: str, headings: dict[str, str]) -> None:
        if not table_name or not isinstance(table_name, str): raise ValueError("Table name must be a non-empty string.")
        if not headings: raise ValueError("Headings dictionary cannot be empty.")
        if not isinstance(headings, dict): raise TypeError("Headings must be a dictionary.")
        
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name}({", ".join([f"{pair} {headings[pair]}" for pair in headings])});")

    def raw_execute(self, sql: str, parms: tuple = ()) -> None:
        if not sql: raise ValueError(f"Value 'sql' can not be empty")
        try: self.cur.execute(sql, parms)
        except sqlite3.Error as e: raise sqlite3.Error(f"Error encounetred whilst running ({sql}): {e}")

    def insert_data(self, table_name: str, data: tuple[Any, ...])-> None:
        if not data: raise ValueError(f"Warning: No data provided for batch insertion into '{table_name}'. Skipping."); return None
        self.cur.execute(f"INSERT INTO {table_name} VALUES({", ".join(["?"] * len(data))})", data)

    def insert_batch_data(self, table_name: str, data: tuple[tuple[Any, ...], ...]) -> None:
        if not data: raise ValueError(f"Warning: No data provided for insertion into '{table_name}'. Skipping."); return None
        self.cur.executemany(f"INSERT INTO {table_name} VALUES({", ".join(["?"] * len(data[0]))})", data)

class Gemini_Ai:
    def __init__(self, api: Api_Manager):
        self.api = api
        self.client: genai.Client = None

    def prompt_the_ai(self, user_prompt) -> str:
        if not self.client:
            self.client = genai.Client(api_key=self.api.get_valid_keys_from_db())

        response = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),)

        return response.text
    
    

class Mistral_Ai:
    def __init__(self, api):
        self.__api = api
        self.__client: Mistral = None

    def generate_text(self, messages: list[dict[str, str]]) -> str:
        if not self.__client:
            self.__client = Mistral(api_key=self.__api)
        response = self.__client.chat.complete(
            model= "mistral-large-2407",
            messages = [
                {
                    "role": mes_obj.get('role'),
                    "content": mes_obj.get('content')
                } for mes_obj in messages
            ]
        )
        return response.model_dump_json()
    
def main():
    if os.path.exists("main.db"):os.remove("main.db")
    os.system("cls" if sys.platform.startswith('win') else "clear")
    gemini = Gemini_Ai(Api_Manager("gemini.env"))
    print(gemini.prompt_the_ai("Who are you? Be brief and short"))

if __name__ == "__main__":
    main()
