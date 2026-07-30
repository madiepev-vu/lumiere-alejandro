from bert_score import score

def generate_quality_score(generated: str, ground_truth: str) -> float:
    _, _, f1 = score(
        [generated],
        [ground_truth],
        lang="en"
    )

    return f1.item()


def generate_quality_scores(generated, ground_truth):
    _, _, f1 = score(generated, ground_truth, lang="en")
    return f1.tolist()