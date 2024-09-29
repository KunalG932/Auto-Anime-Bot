import json
import logging
from typing import Dict, Any
from pyrogram import Client
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logging.txt')
    ]
)
LOG = logging.getLogger('AutoAnimeBot')

# Load configuration
CONFIG_PATH = "./AAB/config.json"

def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_PATH, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        LOG.critical(f"Configuration file not found: {CONFIG_PATH}")
        raise
    except json.JSONDecodeError:
        LOG.critical(f"Invalid JSON in configuration file: {CONFIG_PATH}")
        raise

Vars = load_config()

# Log author and license information
LOG.info(f"Written By: {Vars.get('Author', 'Unknown')}")
LOG.info(f"Licensed Under: {Vars.get('Licensed_under', 'Unknown')}")

# Required configuration keys
REQUIRED_KEYS = [
    'production_chat', 'files_channel', 'main_channel', 'owner',
    'database_url', 'api_id', 'api_hash', 'main_bot', 'client_bot',
    'thumbnail_url'
]

# Validate configuration
missing_keys = [key for key in REQUIRED_KEYS if key not in Vars]
if missing_keys:
    LOG.critical(f"Missing required configuration keys: {', '.join(missing_keys)}")
    raise ValueError("Incomplete configuration")

# Create a Config object for easy access to configuration values
class Config:
    production_chat = Vars['production_chat']
    file_channel = Vars['files_channel']
    main_channel = Vars['main_channel']
    owner = Vars['owner']
    db_uri = Vars['database_url']
    api_id = Vars['api_id']
    api_hash = Vars['api_hash']
    main_bot_token = Vars['main_bot']
    client_bot_token = Vars['client_bot']
    thumbnail_url = Vars['thumbnail_url']

# Post message template
POST_MESSAGE = """
🔸 {}
➖〰️➖〰️➖〰️➖〰️➖〰️
🔸 Episode - {}
〰️➖〰️➖〰️➖〰️➖〰️➖
🔸 Status - {}
➖〰️➖〰️➖〰️➖〰️➖〰️
🔸 Quality - Sub
〰️➖〰️➖〰️➖〰️➖〰️➖
"""

# Initialize Pyrogram clients
file_client = Client(
    "FileBot",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
    bot_token=Config.client_bot_token
)

bot = Client(
    "mainbot",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
    bot_token=Config.main_bot_token
)

# Initialization function
def initialize_bot():
    LOG.info("Initializing bot...")
    # Add any additional initialization steps here
    LOG.info("Bot initialization complete.")

if __name__ == "__main__":
    initialize_bot()
    LOG.info("Configuration loaded successfully.")
    LOG.info(f"Main bot username: {bot.get_me().username}")
    LOG.info(f"File bot username: {file_client.get_me().username}")
