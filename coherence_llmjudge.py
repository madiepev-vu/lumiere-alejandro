import json
import os
from google import genai
from google.genai import types
import keys

client = genai.Client(api_key=keys.coherence_key)

with open("coherence_prompt.txt", "r", encoding="utf-8") as f:
    template_prompt = f.read()

def generate_coherence_score(generated_summary):
    summ = generated_summary

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
    raw_text = response.text 
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean_text)
    normalized_score = float(data["score"])/5.0
    return normalized_score