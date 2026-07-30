import torch
from summac.model_summac import SummaCConv

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SummaCConv(models=["vitc"], device=device)


def generate_factuality_score(source_document, generated_summary):
    return generate_factuality_scores([source_document], [generated_summary])[0]


def generate_factuality_scores(source_documents, generated_summaries):
    imager = model.imagers[0]
    scored_summaries = [
        " ".join(imager.split_sentences(summary)[:model.n_rows])
        for summary in generated_summaries
    ]
    images = imager.build_images(
        source_documents,
        scored_summaries,
        batch_size=32,
    )
    with torch.no_grad():
        logits, _, _ = model.forward(
            source_documents,
            scored_summaries,
            images=images,
        )
    return torch.nn.functional.softmax(logits, dim=-1)[:, 1].tolist()