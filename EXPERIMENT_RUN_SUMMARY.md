# Experiment Run Summary

## Goal

Run every prompting technique against every textbook chapter, evaluate each generated summary, and store both detailed and aggregate results.

The completed experiment contains:

- 5 prompting techniques
- 50 textbook chapter JSON files
- 250 unique prompt-textbook cases

## Work Completed

### Pipeline repair

- Fixed the input contract between the experiment runner and summary generator.
- Added prompt rendering that supports the inconsistent placeholders used across the five prompt templates.
- Preserved prompt templates that do not contain a source-text placeholder by appending the required textbook content.
- Added deterministic sorting for numbered textbook files.

### Microsoft Foundry migration

- Replaced the unavailable Google Gemini integration with the existing Microsoft Foundry deployment.
- Added `azure_model.py` as the shared OpenAI Responses API client.
- Used the `gpt-5.4-mini` deployment for summary generation and LLM-based evaluation.
- Configured low reasoning effort and bounded output sizes.
- Added strict JSON schemas for structured coherence and factuality responses.
- Kept credentials in the ignored `keys.py` file; no credential is stored in the result files or this document.

### Prompt and metric evaluation

- Generated all 250 summaries.
- Evaluated coherence with an LLM judge using the existing 1-5 rubric, normalized to the range 0-1.
- Evaluated quality with batched BERTScore against each chapter's ground-truth objectives.
- Initially used SummaC `vitc` for factuality and tested CPU and Apple MPS execution.
- Added batched SummaC scoring and an exact optimization that limits generated summaries to the first 10 sentences used by SummaC's classifier.
- Preserved that implementation in `factuality_summac.py` for reproducibility.

### Performance investigation

SummaC was the main bottleneck. Its NLI stage compares up to 100 source sentences with 10 generated-summary sentences for each summary. One five-summary textbook batch took approximately 1 hour and 44 minutes, and even reduced-model experiments remained impractical for the complete dataset.

With approval, factuality scoring was changed to a batched Microsoft Foundry LLM judge. One request evaluates all five summaries for a textbook while sending the source chapter only once. A five-summary smoke test completed in 17.5 seconds.

This is a methodology change: the final factuality values are LLM-judge scores, not SummaC scores. All 250 final rows use the same backend, `azure-gpt-5.4-mini`, so the completed dataset does not mix factuality methodologies.

### Reliability and resumability

- Split execution into generation and scoring phases.
- Checkpointed generation after every prompt-textbook case.
- Checkpointed metrics after every textbook.
- Made reruns skip completed work when the expected factuality backend matches.
- Tagged each detailed row with its factuality backend and device.
- Preserved all generated summaries and coherence scores while changing factuality backends.

## Final Scoring Formula

The combined score is:

$$
0.45 \times \text{factuality}
+ 0.30 \times \text{quality}
+ 0.25 \times \text{coherence}
$$

All component values are normalized to the range 0-1.

## Final Outputs

- `results/results_1_details.csv`: one row per prompt-textbook case, including generated summary, component scores, combined score, and factuality backend metadata.
- `results/results_1.csv`: a 5-by-50 matrix of combined scores, with prompting techniques as rows and textbooks as columns.

Final integrity checks:

| Check | Result |
| --- | ---: |
| Detailed rows | 250 |
| Unique prompt-textbook cases | 250 |
| Missing factuality scores | 0 |
| Missing quality scores | 0 |
| Missing coherence scores | 0 |
| Missing combined scores | 0 |
| Aggregate matrix shape | 5 x 50 |
| Missing aggregate values | 0 |
| Factuality backend | `azure-gpt-5.4-mini` for all 250 rows |

Observed score ranges:

| Metric | Minimum | Maximum |
| --- | ---: | ---: |
| Factuality | 0.5000 | 1.0000 |
| Quality | 0.0000 | 0.8384 |
| Coherence | 0.5000 | 1.0000 |
| Combined | 0.6375 | 0.9515 |

One chapter produced BERTScore's `Empty reference sentence` warning. BERTScore handled it by assigning a raw score of zero, and the experiment completed normally. The repeated RoBERTa pooler initialization messages were model warnings rather than experiment failures.

## Validation Performed

- Confirmed the Foundry deployment with an `OK` smoke response.
- Rendered all five prompt templates successfully.
- Compiled the modified Python modules.
- Confirmed no editor diagnostics in `experiment.py`, `factuality.py`, or `factuality_summac.py`.
- Verified 250 complete and unique detailed records.
- Verified the final matrix contains all 250 combined scores.
- Confirmed the experiment process exited and no scoring job remains active.

## Running Again

From the repository root, use the workspace virtual environment:

```bash
./.venv/bin/python3.12 experiment.py
```

The runner detects completed result sets. A fully completed run causes it to select the next experiment number; an interrupted run resumes from its detailed checkpoint.

The VS Code command sandbox denied the virtual-environment symlink with exit code 126 during one test. Running the interpreter directly outside that restricted wrapper resolved the issue; it was not an application or Azure failure.

## Current Architecture

| File | Responsibility |
| --- | --- |
| `azure_model.py` | Shared Microsoft Foundry Responses API client |
| `generate_summary.py` | Prompt rendering and summary generation |
| `coherence_llmjudge.py` | Structured LLM coherence evaluation |
| `factuality.py` | Batched structured LLM factuality evaluation |
| `factuality_summac.py` | Preserved local SummaC implementation |
| `quality.py` | Batched BERTScore quality evaluation |
| `experiment.py` | Resumable orchestration, checkpointing, and result export |

## Important Methodology Note

The repository README describes the original Gemini and SummaC pipeline and is now outdated. The completed result set documented here uses Microsoft Foundry `gpt-5.4-mini` for summary generation, coherence judging, and factuality judging, with BERTScore retained for quality evaluation.
