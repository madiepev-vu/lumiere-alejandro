import os
import json
from google import genai
import keys

client = genai.Client(api_key=keys.summary_key)

with open("openstax_chapter_2_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

original_text = dataset["full_chapter_text"]

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Generate a summary of the following text: " + original_text
)

ans = response.text
dataset["generated_summary"] = ans
with open("openstax_chapter_2_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)
print(ans)