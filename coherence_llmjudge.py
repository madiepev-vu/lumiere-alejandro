import json
from pathlib import Path

from azure_model import generate_json

with open(Path(__file__).resolve().parent / "coherence_prompt.txt", "r", encoding="utf-8") as f:
    template_prompt = f.read()

COHERENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "reason": {"type": "string"},
    },
    "required": ["score", "reason"],
    "additionalProperties": False,
}

def generate_coherence_score(generated_summary):
    summ = generated_summary

    final_prompt = template_prompt.format(
        summary = summ
    )

    raw_text = generate_json(
        final_prompt,
        schema=COHERENCE_SCHEMA,
        max_output_tokens=300,
    )
    data = json.loads(raw_text)
    normalized_score = float(data["score"] - 1)/4.0
    return normalized_score