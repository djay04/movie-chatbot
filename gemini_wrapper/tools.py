import requests
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import psycopg2
from database import add_to_watchlist as db_add_to_watchlist, get_watchlist as db_get_watchlist

load_dotenv()

class Movie(BaseModel):

    imdbID: str
    title: str
    year: str
    genre: str
    poster: str


def search_movies(query: str):

    api_key = os.getenv("OMDB_API")
    params = {"s": query, "apikey": api_key}

    response = requests.get("http://www.omdbapi.com/", params=params)

    print(f"API key: {api_key}")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")

    if response.status_code == 200:
        
        r = response.json()

        movies = []
        for movie in r["Search"]:
            new_response = {"title": movie["Title"],
                            "year": movie["Year"],
                            "genre": "N/A",
                            "poster": movie["Poster"],
                            "imdbID": movie["imdbID"]}
            
            movies.append(new_response)

        return movies
    else:

        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
        raise ValueError(f"Could not search for movies with query: {query}")
        
    

def add_to_watchlist(user_id: int, imdbID: str):

    api_key = os.environ["OMDB_API"]

    response = requests.get(f"https://www.omdbapi.com/?i={imdbID}&apikey={api_key}")

    if response.status_code == 200:
        print(f"Successfully got movie details for user: {user_id}")
    else:
        raise ValueError(f"Response status code -> {response.status_code}")

    data = response.json()

    try:
        db_add_to_watchlist(user_id, imdbID, data["Title"], data["Genre"], data["Year"], data["Poster"])
        title = data["Title"]
        return {"success": f"Added {title} to {user_id}'s watch list"}
    except psycopg2.Error as e:
        return {"error": str(e)} 

def get_watchlist(user_id: int):

    try:

        watchlist = db_get_watchlist(user_id)

        return watchlist
    except psycopg2.Error as e:

        raise ValueError(f"Error getting watchlist: {e}")