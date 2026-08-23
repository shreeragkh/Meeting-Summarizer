"""Audio/video -> transcript, via OpenAI's hosted Whisper API."""

import os
from openai import OpenAI
from .config import config
from .utils import is_video_file, extract_audio_from_video, cleanup_temp_file

_client = OpenAI(api_key=config.OPENAI_API_KEY)


class TranscriptionError(Exception):
    """Raised when a file can't be transcribed (e.g. too large)."""


def transcribe_audio(file_path: str, original_filename: str) -> str:
    """
    Accepts a local file path (audio or video). Extracts audio first if
    the source is a video file. Sends the result to the Whisper API and
    returns the transcript text. Cleans up any temp audio file it creates.
    """
    audio_path = file_path
    temp_audio_created = False

    if is_video_file(original_filename):
        audio_path = extract_audio_from_video(file_path)
        temp_audio_created = True

    try:
        max_bytes = config.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024
        file_size = os.path.getsize(audio_path)
        if file_size > max_bytes:
            raise TranscriptionError(
                f"Audio file is {file_size / (1024*1024):.1f} MB, which exceeds "
                f"the {config.MAX_AUDIO_FILE_SIZE_MB} MB Whisper API limit."
            )

        with open(audio_path, "rb") as audio_file:
            transcript = _client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file,
            )
        return transcript.text
    finally:
        if temp_audio_created:
            cleanup_temp_file(audio_path)