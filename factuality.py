import json

from azure_model import MODEL_DEPLOYMENT, generate_json

backend = f"azure-{MODEL_DEPLOYMENT}"
device = "azure"

FACTUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "evaluations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "summary_index": {"type": "integer", "minimum": 0},
                    "score": {"type": "integer", "minimum": 1, "maximum": 5},
                    "reason": {"type": "string"},
                },
                "required": ["summary_index", "score", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["evaluations"],
    "additionalProperties": False,
}


def generate_factuality_score(source_document, generated_summary):
    return generate_factuality_scores([source_document], [generated_summary])[0]


def generate_factuality_scores(source_documents, generated_summaries):
    if len(source_documents) != len(generated_summaries):
        raise ValueError("Each summary must have a corresponding source document.")
    if not generated_summaries:
        return []
    if len(set(source_documents)) != 1:
        return [
            generate_factuality_score(source, summary)
            for source, summary in zip(source_documents, generated_summaries)
        ]

    summaries = "\n\n".join(
        f"<summary index=\"{index}\">\n{summary}\n</summary>"
        for index, summary in enumerate(generated_summaries)
    )
    prompt = f"""Evaluate the factual consistency of each summary against the source document.

Judge only claims that appear in a summary. Do not penalize omitted source material. A claim is
factual when the source supports it directly or by clear implication. Penalize contradictions,
unsupported specifics, invented causal links, and attribution errors.

Use this scale:
1 = almost all substantive claims are contradicted or unsupported
2 = major factual problems substantially outweigh supported content
3 = a mixture of supported content and meaningful factual problems
4 = nearly all claims are supported, with only minor factual issues
5 = all substantive claims are supported and no contradictions are present

Return exactly one evaluation for every summary, in ascending summary_index order.

<source_document>
{source_documents[0]}
</source_document>

{summaries}
"""
    raw_text = generate_json(
        prompt,
        schema=FACTUALITY_SCHEMA,
        max_output_tokens=1200,
    )
    evaluations = json.loads(raw_text)["evaluations"]
    if [item["summary_index"] for item in evaluations] != list(range(len(generated_summaries))):
        raise ValueError("Factuality judge returned incomplete or out-of-order evaluations.")
    return [(item["score"] - 1) / 4.0 for item in evaluations]