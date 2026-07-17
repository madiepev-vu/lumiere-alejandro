import json
from summac.model_summac import SummaCConv
model = SummaCConv(models=["vitc"], device="cpu")


def generate_factuality_score(source_document, generated_summary):
    score = model.score(
        [source_document],
        [generated_summary]
    )

    return score["scores"][0]