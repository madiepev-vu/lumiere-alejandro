import os
import json
from google import genai
from google.genai import types
import keys

client = genai.Client(api_key=keys.summary_key)


def generate_summary(prompt , text_json):
    file = json.loads(text_json)
    original_text = file["full_chapter_text"]
    topic = file["topic"]
    content = prompt.format(original_text=original_text, topic=topic)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents= content,
        config=types.GenerateContentConfig(
            temperature=0.0,
        ),
    )
    return response.text