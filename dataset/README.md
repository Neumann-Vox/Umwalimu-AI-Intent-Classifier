# Umwalimu AI — Intent Classifier (Portfolio Project 2, Part 1)

This folder contains the technical Part 1 artefacts for the Umwalimu AI educational-assistant intent classifier.

## Required files
| File | Purpose |
|---|---|
| `intents.csv` | Labelled messages with reproducible train/test split |
| `Portfolio_Project_2_Part_1_Classifier.ipynb` | Dataset audit, baseline, model training, evaluation, threshold analysis and saving |
| `intent_classifier.joblib` | Saved scikit-learn pipeline |
| `README.md` | Dataset provenance, measured results and limitations |

## Intent labels
There are six balanced labels, 30 messages each.

| Intent | Meaning |
|---|---|
| `explain_concept` | Definition, explanation or clarification of a learning concept |
| `solve_problem` | Help solving a particular exercise, calculation or problem |
| `practice_request` | Exercises, quizzes, tests or revision questions |
| `check_answer` | Verify, mark or correct an attempted answer |
| `learning_guidance` | Study planning, revision guidance or learning support |
| `out_of_scope` | Outside the intended educational-assistant tasks |

## Dataset audit and provenance
The CSV contains 180 rows with `text`, `intent`, `source` and `split` fields. The notebook checks required values, empty messages, class balance and duplicates (normalising text only for duplicate detection).

- 180 messages total; 30 per intent.
- No missing values in required fields.
- No duplicate messages after normalisation.
- Every current row has `source=written`.

**Important:** these are manually composed development examples, not verified messages collected from 20 real people. Do not represent them as participant submissions. The actual Portfolio Project 1 Step 10 local-phrasing records and `UNMATCHED` log were not supplied. The instructor's Assignment 8 written feedback was also not supplied, so feedback-specific changes cannot be claimed as complete.

## Train/test split
The notebook recreates a stratified 80/20 split with `train_test_split`, `random_state=42`:
- Training: 144 messages (24 per intent).
- Test: 36 messages (6 per intent).

The notebook writes this split to `intents.csv` when run.

## Classifier training
Both models are fitted using training data only:
1. **Words:** default word-level `TfidfVectorizer` + `LogisticRegression(max_iter=1000, random_state=42)`.
2. **Characters:** `TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))` + the same Logistic Regression configuration.

### Test-set comparison (36 messages)
| Features | Accuracy | Macro precision | Macro recall | Macro F1 |
|---|---:|---:|---:|---:|
| Words | **77.78%** | **79.96%** | **77.78%** | **77.11%** |
| Characters (768 max features) | 77.78% | 79.54% | 77.78% | 76.76% |

The word model was selected because both candidates tied on accuracy, while the word model achieved the higher macro F1. The character vectorizer is capped at 768 features to keep its comparison compact. Selection uses macro F1, with accuracy as the tie-breaker. These results are preliminary because the test set is small.

### Per-intent results

The notebook generates the classification report and confusion matrix from the selected model when executed. Use those notebook outputs as the source for per-intent metrics; they are not duplicated here, so the README cannot drift from the model actually selected.

## Confidence threshold
The selected threshold is **0.25**. Compared with threshold 0.20, it reduces confident wrong predictions from 6 to 3, with 5 fewer correct predictions (28 to 23), 8 more missed requests (2 to 10), and a 41.7% fallback rate (15 of 36). This is a compromise between avoiding incorrect intent routing and retaining useful coverage; it should be re-evaluated on a larger genuine dataset.

## Rules comparison — limitation
The original Portfolio Project 1 chatbot rules were not available. The notebook therefore uses a **provisional dataset-derived keyword baseline**, not the original Umwalimu AI chatbot rules.

| System | Right | Missed | Wrong |
|---|---:|---:|---:|
| Provisional dataset-derived rules | 23 | 13 | 0 |
| Word classifier at threshold 0.25 | 23 | 10 | 3 |

This comparison describes only the provisional baseline. It does not establish that the classifier outperforms the original chatbot rules.

## Reproduce and load the model
Install:
```bash
python -m pip install pandas scikit-learn joblib matplotlib jupyter
```
Open the notebook from the repository root and run all cells. To load the model:
```python
import joblib
classifier = joblib.load("dataset/intent_classifier.joblib")
message = "Can you explain what a variable is?"
print(classifier.predict([message])[0])
print(classifier.predict_proba([message]).max())
```
The preparation environment used scikit-learn 1.8.0. Use a compatible version when loading a joblib model; scikit-learn does not guarantee cross-version compatibility.

## Outstanding assignment evidence
1. **20+ genuine messages from real people:** not supplied; the current messages are manually composed development examples.
2. **Assignment 8 written feedback:** not supplied; feedback-specific improvements cannot be verified.
3. **Portfolio Project 1 `UNMATCHED` log and Step 10 local-phrasing records:** not supplied.
4. **Original Portfolio Project 1 rules:** not supplied; the comparison is provisional.

Do not claim these requirements are complete until the original evidence is collected. Do not publish participant names, phone numbers, identity numbers or credentials.
