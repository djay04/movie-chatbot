import requests
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

    if response.status_code == 200:
        
        r = response.json()

        movies = []
        for movie in r["Search"]:
            new_response = {"title": movie["Title"],
                            "year": movie["Year"],
                            "genre": movie["Genre"],
                            "poster": movie["Poster"],
                            "imdbID": movie["imdbID"]}
            
            movies.append(new_response)

        return movies
    else:
        raise ValueError(f"Could not search for movies with query: {query}")
    

def add_to_watchlist(user_id: int, movie: Movie):

    try:
        db_add_to_watchlist(user_id, movie.imdbID, movie.title, movie.genre, movie.year, movie.poster)
        
        return {"success": f"Added {movie} to {user_id}'s watch list"}
    except psycopg2.Error as e:
        return {"error": e} 

def get_watchlist(user_id: int):

    try:

        watchlist = db_get_watchlist(user_id)

        return watchlist
    except psycopg2.Error as e:

        raise ValueError(f"Error getting watchlist: {e}")