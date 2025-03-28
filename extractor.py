import os
from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel
from typing import List

class WorkoutData(BaseModel):
    exercise: str
    reps: int
    weight: float
    muscles: List[str]
    date: str

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_workout_data(transcript: str) -> WorkoutData:
    today = datetime.today().strftime("%Y-%m-%d")
    
    prompt = f"""
Extract the following workout data from the transcription below.
Output a valid JSON object that conforms exactly to this schema:
  - "exercise": (string) the name of the exercise.
  - "reps": (integer) the number of repetitions.
  - "weight": (number) the weight used in pounds.
  - "muscles": (array of strings) the primary muscle groups targeted. If the muscle is mentioned in the name of the exercise include just that muscle. If not, include the primary muscle groups targeted by the exercise.
  - "date": (string) today's date in YYYY-MM-DD format, which should be "{today}".

Do not include any extra text, markdown, or formatting. Output only the JSON object.

Transcription: "{transcript}"
"""
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a workout data extractor. Extract the workout data strictly according to the provided schema."},
            {"role": "user", "content": prompt}
        ],
        response_format=WorkoutData,
    )
    
    workout_data = completion.choices[0].message.parsed
    return workout_data
