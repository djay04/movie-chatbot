import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

db_url = os.getenv('DATABASE_URL')

def init_db():
    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id serial PRIMARY KEY, email varchar, password varchar);")

    cur.execute("CREATE TABLE IF NOT EXISTS movie (movie_id serial PRIMARY KEY, title varchar, poster_url varchar, year varchar, genre varchar);")

    conn.commit()

    try:
        cur.execute("CREATE TYPE status AS ENUM ('watched', 'in-progress', 'not started yet');")
        conn.commit()
    except psycopg2.errors.DuplicateObject:
        conn.rollback()

    cur.execute("CREATE TABLE IF NOT EXISTS watchlist (watchlist serial PRIMARY KEY, w_userid integer REFERENCES users(user_id), w_movieid integer REFERENCES movie(movie_id), movie_status status);")

    conn.commit()
    cur.close()
    conn.close()

def add_to_watchlist(user_id, movie_id, title, genre, year, poster_url):

    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("INSERT INTO movie (movie_id, title, poster_url, year, genre) VALUES (%s,%s,%s,%s,%s)  ON CONFLICT (movie_id) DO NOTHING;", 
                (movie_id, title, poster_url, year, genre))


    cur.execute("INSERT INTO watchlist (w_userid, w_movieid, movie_status) VALUES (%s, %s, %s);",
                (user_id, movie_id, "Not started yet"))
    
    conn.commit()
    cur.close()
    conn.close()