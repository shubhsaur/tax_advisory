import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv  # Correct import for loading .env files
 
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../..', '.env'))
 
# Parse the SUPABASE_URL to extract connection parameters
# Example: postgres://user:password@host:port/dbname
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_DATABASE = os.getenv("SUPABASE_DBNAME")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")

def get_connection():
    return psycopg2.connect(
            host=SUPABASE_HOST,
            dbname=SUPABASE_DATABASE,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT
    )
