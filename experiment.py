import pandas as pd
import json
import coherence_llmjudge
import factuality
import generate_summary
import quality
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
textbooks_DIR = BASE_DIR / "textbooks"
prompting_DIR = BASE_DIR / "prompting_techniques"
results_DIR = BASE_DIR / "results"

columns = []
rows = []

for archivo in sorted(textbooks_DIR.glob("*.json"), key=lambda p: (p.stem.split("_")[0:-1], int(p.stem.split("_")[-1]))):
    columns.append(archivo.stem)
    print(archivo.stem)

for archivo in sorted(prompting_DIR.glob("*.txt")):
    rows.append(archivo.stem)
    print(archivo.stem)

DF_results = pd.DataFrame(index=rows, columns=columns)

for prompt_file in sorted(prompting_DIR.glob("*.txt")):
    for textbook_file in sorted(textbooks_DIR.glob("*.json"), key=lambda p: (p.stem.split("_")[0:-1], int(p.stem.split("_")[-1]))):
        
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read()

        with open(textbook_file, "r", encoding="utf-8") as f:
            textbook = json.load(f)

        #ground_truth_objectives
        #full_chapter_text

        original_text = textbook["full_chapter_text"]
        ground_truth_objectives = textbook["ground_truth_objectives"]
        generated_summary = generate_summary.generate_summary(prompt, original_text)

        coherence_score = coherence_llmjudge.generate_coherence_score(generated_summary)
        factuality_score = factuality.generate_factuality_score(original_text, generated_summary)
        quality_score = quality.generate_quality_score(generated_summary, ground_truth_objectives)

        DF_results.loc[prompt_file.stem, textbook_file.stem] = 0.45 * factuality_score + 0.3 * quality_score + 0.25 * coherence_score

experiment_number = len(list(results_DIR.glob("*.csv"))) + 1

DF_results.to_csv(results_DIR / f"results_{experiment_number}.csv", index=True)