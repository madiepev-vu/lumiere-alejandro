import json
import re
from pathlib import Path

import pandas as pd

import coherence_llmjudge
import factuality
import generate_summary
import quality

BASE_DIR = Path(__file__).resolve().parent
textbooks_DIR = BASE_DIR / "textbooks"
prompting_DIR = BASE_DIR / "prompting_techniques"
results_DIR = BASE_DIR / "results"



def textbook_sort_key(path):
    return path.stem.split("_")[:-1], int(path.stem.split("_")[-1])


prompt_files = sorted(prompting_DIR.glob("*.txt"))
textbook_files = sorted(textbooks_DIR.glob("*.json"), key=textbook_sort_key)
total_cases = len(prompt_files) * len(textbook_files)

result_numbers = []
for path in results_DIR.glob("results_*.csv"):
    match = re.fullmatch(r"results_(\d+)(?:_details)?\.csv", path.name)
    if match:
        result_numbers.append(int(match.group(1)))

experiment_number = max(result_numbers, default=1)
details_file = results_DIR / f"results_{experiment_number}_details.csv"
if details_file.exists():
    details = pd.read_csv(details_file).to_dict("records")
    if len(details) == total_cases and all(row.get("combined") == row.get("combined") for row in details):
        experiment_number += 1
        details = []
else:
    details = []

results_file = results_DIR / f"results_{experiment_number}.csv"
details_file = results_DIR / f"results_{experiment_number}_details.csv"
details_by_case = {(row["prompt"], row["textbook"]): row for row in details}

completed_generation = sum(bool(row.get("summary")) for row in details)
for prompt_file in prompt_files:
    prompt = prompt_file.read_text(encoding="utf-8")
    for textbook_file in textbook_files:
        case = (prompt_file.stem, textbook_file.stem)
        existing = details_by_case.get(case, {})
        if existing.get("summary") and existing.get("coherence") == existing.get("coherence"):
            continue

        textbook = json.loads(textbook_file.read_text(encoding="utf-8"))
        summary = generate_summary.generate_summary(prompt, textbook)
        coherence_score = coherence_llmjudge.generate_coherence_score(summary)
        details_by_case[case] = {
            "prompt": prompt_file.stem,
            "textbook": textbook_file.stem,
            "summary": summary,
            "factuality": None,
            "quality": None,
            "coherence": coherence_score,
            "combined": None,
            "factuality_device": factuality.device,
        }
        pd.DataFrame(details_by_case.values()).to_csv(details_file, index=False)
        completed_generation += 1
        print(f"Generated {completed_generation}/{total_cases}: {prompt_file.stem} x {textbook_file.stem}", flush=True)

for textbook_file in textbook_files:
    textbook = json.loads(textbook_file.read_text(encoding="utf-8"))
    cases = [(prompt_file.stem, textbook_file.stem) for prompt_file in prompt_files]
    if all(
        details_by_case[case].get("combined") == details_by_case[case].get("combined")
        and details_by_case[case].get("factuality_backend") == factuality.backend
        for case in cases
    ):
        continue

    summaries = [details_by_case[case]["summary"] for case in cases]
    factuality_scores = factuality.generate_factuality_scores(
        [textbook["full_chapter_text"]] * len(cases),
        summaries,
    )
    quality_scores = quality.generate_quality_scores(
        summaries,
        [textbook["ground_truth_objectives"]] * len(cases),
    )

    for case, factuality_score, quality_score in zip(cases, factuality_scores, quality_scores):
        row = details_by_case[case]
        row["factuality"] = factuality_score
        row["factuality_backend"] = factuality.backend
        row["factuality_device"] = factuality.device
        row["quality"] = quality_score
        row["combined"] = (
            0.45 * factuality_score
            + 0.3 * quality_score
            + 0.25 * row["coherence"]
        )

    details_frame = pd.DataFrame(details_by_case.values())
    details_frame.to_csv(details_file, index=False)
    results = details_frame.pivot(index="prompt", columns="textbook", values="combined")
    results.to_csv(results_file, index=True)
    print(f"Scored textbook: {textbook_file.stem}", flush=True)