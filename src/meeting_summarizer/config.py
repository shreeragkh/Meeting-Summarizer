"""Centralized configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    WHISPER_MODEL: str = "whisper-1"
    SUMMARY_MODEL: str = "gpt-4o-mini"
    MAX_AUDIO_FILE_SIZE_MB: int = 25
    CHUNK_MAX_CHARS: int = 8000

    @classmethod
    def validate(cls):
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.DATABASE_URL:
            missing.append("DATABASE_URL")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Check your .env file or deployment secrets."
            )


config = Config()