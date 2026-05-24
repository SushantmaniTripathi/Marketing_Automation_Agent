"""
Environment Configuration Module
Loads and validates environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class EnvConfig:
    """Environment configuration handler"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Instagram Account 1 (Gaming)
    ACCOUNT_NAME_1: str = os.getenv('ACCOUNT_NAME_1', 'Gaming Account')
    INSTAGRAM_TOKEN_1: str = os.getenv('INSTAGRAM_TOKEN_1', '')
    INSTAGRAM_ID_1: str = os.getenv('INSTAGRAM_ID_1', '')
    INSTAGRAM_USERNAME_1: str = os.getenv('INSTAGRAM_USERNAME_1', '')
    INSTAGRAM_PASSWORD_1: str = os.getenv('INSTAGRAM_PASSWORD_1', '')
    
    # Instagram Account 2 (Web3)
    ACCOUNT_NAME_2: str = os.getenv('ACCOUNT_NAME_2', 'Web3 Account')
    INSTAGRAM_TOKEN_2: str = os.getenv('INSTAGRAM_TOKEN_2', '')
    INSTAGRAM_ID_2: str = os.getenv('INSTAGRAM_ID_2', '')
    INSTAGRAM_USERNAME_2: str = os.getenv('INSTAGRAM_USERNAME_2', '')
    INSTAGRAM_PASSWORD_2: str = os.getenv('INSTAGRAM_PASSWORD_2', '')
    
    # Project Paths
    PROJECT_ROOT: Path = Path(os.getenv('PROJECT_ROOT', Path(__file__).parent.parent.parent))
    ASSETS_PATH: Path = PROJECT_ROOT / 'assets'
    GENERATED_IMAGES_PATH: Path = PROJECT_ROOT / 'data' / 'generated_images'
    LOGO_PATH: Path = PROJECT_ROOT / 'assets' / 'logos'
    
    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required environment variables are set"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENAI_API_KEY',
            'INSTAGRAM_USERNAME_1',
            'INSTAGRAM_PASSWORD_1',
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_instagram_account(cls, account_num: int = 1) -> dict:
        """Get Instagram account credentials by number (1 or 2)"""
        if account_num == 1:
            return {
                'name': cls.ACCOUNT_NAME_1,
                'token': cls.INSTAGRAM_TOKEN_1,
                'id': cls.INSTAGRAM_ID_1,
                'username': cls.INSTAGRAM_USERNAME_1,
                'password': cls.INSTAGRAM_PASSWORD_1,
            }
        elif account_num == 2:
            return {
                'name': cls.ACCOUNT_NAME_2,
                'token': cls.INSTAGRAM_TOKEN_2,
                'id': cls.INSTAGRAM_ID_2,
                'username': cls.INSTAGRAM_USERNAME_2,
                'password': cls.INSTAGRAM_PASSWORD_2,
            }
        else:
            raise ValueError(f"Invalid account number: {account_num}. Must be 1 or 2.")


# Create singleton instance
env_config = EnvConfig()
