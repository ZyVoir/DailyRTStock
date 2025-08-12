import os
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client(isProd : bool = False) -> Client:
    DB_URL = "DB_URL"
    DB_KEY = "DB_KEY"
    url = ""
    key = ""
    if isProd:
        url = os.environ[DB_URL]
        key = os.environ[DB_KEY]
    else:
        load_dotenv()
        url = os.getenv(DB_URL)
        key = os.getenv(DB_KEY)

    return create_client(url, key)
