import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv


ALGORITHM = "HS256"

load_dotenv()


def hash_password(password):

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hashed.decode("utf-8")


def verify_password(plain, hashed):

    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")

    return bcrypt.checkpw(plain.encode("utf-8"), hashed)


def create_token(user_id):

    secret_key = os.environ["SECRET_KEY"]

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {"user_id": user_id, "exp": expire}

    encoded_jwt = jwt.encode(payload, secret_key,algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token):

    secret_key = os.environ["SECRET_KEY"]

    try:

        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM   ])

        return payload["user_id"]
    except Exception as e:

        raise ValueError(f"Error when verifying token -> {e}")
