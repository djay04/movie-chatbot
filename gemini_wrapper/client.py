from dotenv import load_dotenv
import os
from groq import Groq
import json
from typing import List
from gemini_wrapper.tools import search_movies as cli_search_movies, get_watchlist as cli_get_watchlist, add_to_watchlist as cli_add_to_watchlist, Movie


load_dotenv()


class MovieBot:

    def __init__(self):
        groq_api_key = os.environ["GROQ_API"]


        self.client = Groq (
            api_key=groq_api_key
        )

        # groq is stateless, chat history isn't remembered
        self.chat_history = [{
            "role": "system", "content": "You are a helpful assistant with access to add to a movie watch list, get a movie watchlist, and suggest movies to user based on prompt flow. Be warm and helpful."
        }]

        self.tools = [
                    {
                "type": "function",
                "function": {
                    "name": "search_movies",
                    "description": "Search for movies based on a user query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search term e.g. sci-fi, Interstellar, Tom Hanks movies"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_watchlist",
                    "description": "Add a movie to the user's watchlist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "The user's ID"},
                            "imdbID": {"type": "string", "description": "The movie's IMDB ID"}
                        },
                        "required": ["user_id", "imdbID"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_watchlist",
                    "description": "Get the user's movie watchlist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "The user's ID"}
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ]
    
    def send_message(self, user_input: str):

        self.chat_history.append({
            "role": "user", "content": user_input
        }
        )

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.chat_history,
            tools=self.tools,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments

            self.chat_history.append({
                "role": "assistant", "content": None, "tool_calls": [{
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": arguments
                    }
                }]
            })

            data = json.loads(arguments)

            result = None
            if function_name == "add_to_watchlist":


                result = cli_add_to_watchlist(data["user_id"], data["imdbID"])

            elif function_name == "get_watchlist":

                result = cli_get_watchlist(data["user_id"])

            elif function_name == "search_movies":

                result = cli_search_movies(data["query"]) 
            
            
            json_result = json.dumps(result)

            self.chat_history.append({
                "role": "tool", "tool_call_id": tool_call.id, "name": function_name, "content": json_result
            })

            second_response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.chat_history,
            )

            return second_response.choices[0].message.content

        else:

            self.chat_history.append({
                "role": "assistant", "content": response.choices[0].message.content
            })


        return response.choices[0].message.content

        


