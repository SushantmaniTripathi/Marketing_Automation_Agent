"""
Application Constants
"""

# Bot Commands
BOT_COMMANDS = {
    'START': '/start',
    'HELP': '/help',
    'GENERATE': '/generate',
    'POST': '/post',
    'STATUS': '/status',
    'SETTINGS': '/settings',
}

# Instagram Settings
INSTAGRAM_MAX_CAPTION_LENGTH = 2200
INSTAGRAM_MAX_HASHTAGS = 30
INSTAGRAM_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']

# AI Settings
DALLE_IMAGE_SIZE = "1024x1024"
DALLE_QUALITY = "standard"
DALLE_STYLE = "vivid"

# File Paths (relative to project root)
LOGO_DECENTRAWOOD = "assets/logos/DECENTRAWOOD.png"
LOGO_DEOD = "assets/logos/deod.png"

# Timeouts
REQUEST_TIMEOUT = 30  # seconds
SELENIUM_TIMEOUT = 20  # seconds

# Retry Settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
