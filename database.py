import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

db_url = os.getenv('DATABASE_URL')

def init_db():
    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id serial PRIMARY KEY, email varchar, password varchar);")

    cur.execute("CREATE TABLE IF NOT EXISTS movie (movie_id varchar PRIMARY KEY, title varchar, poster_url varchar, year varchar, genre varchar);")

    conn.commit()

    try:
        cur.execute("CREATE TYPE status AS ENUM ('watched', 'in-progress', 'not started yet');")
        conn.commit()
    except psycopg2.errors.DuplicateObject:
        conn.rollback()

    cur.execute("CREATE TABLE IF NOT EXISTS watchlist (watchlist serial PRIMARY KEY, w_userid integer REFERENCES users(user_id), w_movieid varchar REFERENCES movie(movie_id), movie_status status);")

    conn.commit()
    cur.close()
    conn.close()

def add_to_watchlist(user_id, movie_id, title, genre, year, poster_url):

    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    print(f"Inserting movie: {movie_id}, {title}")
    cur.execute("INSERT INTO movie (movie_id, title, poster_url, year, genre) VALUES (%s,%s,%s,%s,%s)  ON CONFLICT (movie_id) DO NOTHING;", 
                (movie_id, title, poster_url, year, genre))
    print(f"Movie Inserted")
    cur.execute("INSERT INTO watchlist (w_userid, w_movieid, movie_status) VALUES (%s, %s, %s);",
                (user_id, movie_id, "not started yet"))
    print(f"Watchlist inserted")
    conn.commit()
    cur.close()
    conn.close()

def get_watchlist(user_id):

    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("SELECT m.title, m.year, m.genre FROM movie m JOIN watchlist w ON w.w_movieid = m.movie_id WHERE w.w_userid = %s;", (user_id,))
    
    rows = cur.fetchall()

    results = []
    for tuple in rows:

        record = {
            "title": tuple[0],
            "year": tuple[1],
            "genre": tuple[2]
        }

        results.append(record)
    

    cur.close()
    conn.close()

    return results

def create_user(email, hash):

    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING user_id", (email, hash))

    user_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return user_id

def get_user_by_email(email):

    conn = psycopg2.connect(db_url)

    cur = conn.cursor()

    cur.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))

    user_id, password = cur.fetchone()

    conn.close()
    cur.close()

    return user_id, password