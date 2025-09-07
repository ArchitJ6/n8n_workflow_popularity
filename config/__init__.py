import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Mode settings
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'True').lower() in ('true', '1', 't')