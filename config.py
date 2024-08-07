from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the token
access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
