from openai import OpenAI
api_key = "sk-YOURAPIKEY"

client = OpenAI(api_key=api_key)

with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language="en", # change to like ja for japanese, or leave empty to "guess"
    )
    print(transcription.text)