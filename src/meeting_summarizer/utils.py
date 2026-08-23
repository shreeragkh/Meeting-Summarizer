"""Helper functions: video-to-audio extraction, transcript chunking, cleanup."""

import os
from moviepy import VideoFileClip
from .config import config

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def is_video_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in VIDEO_EXTENSIONS


def extract_audio_from_video(video_path: str, output_path: str | None = None) -> str:
    """Extracts the audio track from a video file, saves as .mp3, returns the path."""
    if output_path is None:
        output_path = os.path.splitext(video_path)[0] + "_audio.mp3"

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_path, logger=None)
    clip.close()
    return output_path


def chunk_text(text: str, max_chars: int = config.CHUNK_MAX_CHARS) -> list[str]:
    """Splits long text into chunks under max_chars, breaking on sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = f"{current_chunk} {sentence}." if current_chunk else f"{sentence}."
        if len(candidate) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = f"{sentence}."
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def cleanup_temp_file(path: str | None) -> None:
    """Deletes a temp file if it exists, ignoring errors."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass