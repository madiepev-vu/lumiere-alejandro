import os
import json
from google import genai
from google.genai import types
import keys

client = genai.Client(api_key=keys.summary_key)


def generate_summary(prompt , original_text):
    content = prompt.format(original_text=original_text)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents= content,
        config=types.GenerateContentConfig(
            temperature=0.0,
        ),
    )
    return response.text