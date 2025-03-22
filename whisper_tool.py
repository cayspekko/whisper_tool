import os
import math
from openai import OpenAI
import tempfile
import subprocess

MAXIMUM_FILE_SIZE = 25 * 1024 * 1024  # 25MB (slightly less than the API limit for safety)

def chunk_audio(file_path, chunk_size_bytes):
    """Split audio file into chunks of approximately chunk_size_bytes using ffmpeg."""
    file_size = os.path.getsize(file_path)
    if file_size <= chunk_size_bytes:
        return [file_path]
    
    audio_info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path], capture_output=True, text=True)
    duration_sec = float(audio_info.stdout.strip())
    file_count = math.ceil(file_size / chunk_size_bytes)
    chunk_duration = duration_sec / file_count
    
    chunks = []
    with tempfile.TemporaryDirectory(delete=False) as temp_dir:
        for i in range(file_count):
            start_time = i * chunk_duration
            chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
            subprocess.run(['ffmpeg', '-i', file_path, '-ss', str(start_time), '-t', str(chunk_duration), '-c', 'copy', chunk_path, '-y'])
            chunks.append(chunk_path)
    
    return chunks

def transcribe_audio_chunks(file_path, api_key):
    """Transcribe audio file by breaking it into chunks if necessary."""
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    file_size = os.path.getsize(file_path)
    
    # If file is smaller than limit, transcribe directly
    if file_size <= MAXIMUM_FILE_SIZE:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="en",
            )
        return transcription.text
    
    # Otherwise, chunk the file and transcribe each chunk
    chunks = chunk_audio(file_path, MAXIMUM_FILE_SIZE)
    all_transcriptions = []
    
    for chunk_path in chunks:
        with open(chunk_path, "rb") as audio_chunk:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_chunk,
                language="en",
            )
        all_transcriptions.append(transcription.text)
    
    # Combine all transcriptions
    return " ".join(all_transcriptions)

# Main execution
if __name__ == "__main__":
    api_key = "sk-YOURAPIKEY"
    audio_path = "./audio.mp3"
    
    result = transcribe_audio_chunks(audio_path, api_key)
    print(result)