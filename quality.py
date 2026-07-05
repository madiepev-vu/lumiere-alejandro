import json

from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],
    use_stemmer=True
)

with open("openstax_chapter_2_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)
    reference_summary = dataset["full_chapter_text"]
    generated_summary = dataset["generated_summary"]

scores = scorer.score(reference_summary,
                      generated_summary)

print(scores)