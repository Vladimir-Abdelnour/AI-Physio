"""Helper functions for audio transcription using OpenAI Whisper API."""

import asyncio
from pathlib import Path
from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from app_logging import get_logger

logger = get_logger(__name__)

# Maximum file size for Whisper API (25MB)
MAX_FILE_SIZE = 25 * 1024 * 1024

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def transcribe_audio_chunk(audio_path: Path) -> str:
    """
    Transcribe a single audio file using OpenAI Whisper API.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcribed text
        
    Raises:
        Exception: If transcription fails after retries
    """
    logger.info("Starting transcription", audio_path=str(audio_path))
    
    try:
        # Open and read the file
        with open(audio_path, 'rb') as audio_file:
            response = await openai_client.audio.transcriptions.create(
                model=settings.openai_model_whisper,
                file=audio_file,
                response_format="text"
            )
        
        logger.info("Transcription completed successfully", 
                   audio_path=str(audio_path),
                   text_length=len(response))
        
        return response
        
    except Exception as e:
        logger.error("Transcription failed", 
                    audio_path=str(audio_path),
                    error=str(e))
        raise


async def chunk_large_audio(audio_path: Path) -> List[Path]:
    """
    Split large audio files into smaller chunks if they exceed the size limit.
    
    Note: This is a placeholder implementation. In production, you would use
    a library like pydub to split audio files based on time or silence detection.
    
    Args:
        audio_path: Path to the original audio file
        
    Returns:
        List of paths to audio chunks
    """
    file_size = audio_path.stat().st_size
    
    if file_size <= MAX_FILE_SIZE:
        return [audio_path]
    
    logger.warning("Audio file exceeds size limit, chunking required",
                  audio_path=str(audio_path),
                  file_size=file_size,
                  max_size=MAX_FILE_SIZE)
    
    # TODO: Implement actual audio chunking using pydub or similar
    # For now, we'll just return the original file and handle the error
    return [audio_path]


async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file, handling chunking if necessary.
    
    Args:
        audio_path: Path to the audio file to transcribe
        
    Returns:
        Complete transcribed text
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If file format is not supported
    """
    path = Path(audio_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Check file extension
    supported_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
    if path.suffix.lower() not in supported_formats:
        raise ValueError(f"Unsupported audio format: {path.suffix}")
    
    # Check and chunk if necessary
    chunks = await chunk_large_audio(path)
    
    # Transcribe all chunks
    transcripts = []
    for chunk_path in chunks:
        transcript = await transcribe_audio_chunk(chunk_path)
        transcripts.append(transcript)
    
    # Combine all transcripts
    full_transcript = " ".join(transcripts)
    
    logger.info("Full transcription completed",
               audio_path=str(path),
               chunks_processed=len(chunks),
               total_length=len(full_transcript))
    
    return full_transcript
