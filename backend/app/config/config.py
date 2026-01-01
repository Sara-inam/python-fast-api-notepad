import os
from dotenv import load_dotenv

# .env load karo
load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
HF_API_TOKEN = os.getenv("HF_API_TOKEN") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
