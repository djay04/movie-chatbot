from google import genai
from dotenv import load_dotenv
import os
from google.genai import types
from tools import add_to_watchlist, get_watchlist, search_movies


load_dotenv()


class MovieBot:

    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API")

        self.client = genai.Client(api_key=gemini_api_key)

        self.chat = self.client.chats.create(model="gemini-2.0-flash",
                            config=types.GenerateContentConfig(
                                tools=[add_to_watchlist, search_movies, get_watchlist],
                                system_instruction="You are a helpful assistant with access to add to a movie watch list, get a movie watchlist, and suggest movies to user based on prompt flow. Be warm and helpful."
                            ))
    
    def send_message(self, user_input: str):

        response = self.chat.send_message(user_input)

        return response.text

        


