from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os
import io

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file):
    try:
        audio_bytes = audio_file.read()
        audio_file.seek(0)
        transcript_response = client.audio.transcriptions.create(
            model="whisper-1",
            file=("recording.m4a", io.BytesIO(audio_bytes), "audio/m4a")
        )
        text = transcript_response.text
        return text

    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise RuntimeError("Whisper API failed to transcribe the audio.")
