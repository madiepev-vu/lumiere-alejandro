import json
import os
from google import genai
from google.genai import types
import keys

client = genai.Client(api_key=keys.coherence_key)

with open("prompt.txt", "r", encoding="utf-8") as f:
    template_prompt = f.read()

with open("openstax_chapter_2_dataset.json", "r", encoding="utf-8") as f:
    summ = json.load(f)["generated_summary"]


final_prompt = template_prompt.format(
    summary = summ
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=final_prompt,
    config=types.GenerateContentConfig(
        temperature=0.0,
    ),
)

print(response.text)