# Intent dataset: Umwalimu AI

*Assignment 8, the first stage of Portfolio Project 2, Part 1.*

## Try the chat interface

The Streamlit interface lets you enter a message and see the classifier’s predicted learning intent and confidence. This version is a classifier demo: it does not generate explanations, solve problems, create exercises, or check answers yet.

### Run locally on Windows

```powershell
git clone https://github.com/Neumann-Vox/Umwalimu-AI-Intent-Classifier.git
cd Umwalimu-AI-Intent-Classifier
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local address Streamlit prints (usually `http://localhost:8501`). The interface uses the committed model at `dataset/intent_classifier.joblib`.

## The labels

| Label | What it means | Messages |
|---|---|---:|
| `explain_concept` | The student asks for a definition, explanation, teaching or clarification of a learning concept. | 30 |\n| `solve_problem` | The student asks for help solving a specific exercise, calculation or problem. | 30 |\n| `practice_request` | The student requests exercises, quizzes, tests, homework or revision questions. | 30 |\n| `check_answer` | The student asks the assistant to verify, mark or correct an attempted answer. | 30 |\n| `learning_guidance` | The student asks for study planning, revision guidance, progress support or advice on what to learn next. | 30 |\n| `out_of_scope` | The request is outside Umwalimu AI's defined educational learning-support functions. | 30 |\n
## The labelling guideline

1. Assign exactly one intent to each message. If a message contains two independent requests, split it into two rows before labelling.\n2. Use explain_concept when the student asks for a definition, meaning, explanation, comparison, or teaching of a subject/topic without asking to solve a specific supplied exercise.\n3. Use solve_problem when the student provides or refers to a particular question/equation and asks the assistant to work through or solve it.\n4. Use practice_request when the student asks for new exercises, examples to try, a quiz, test, revision questions, or homework practice.\n5. Use check_answer when the student gives an attempted answer or solution and asks whether it is correct, or asks the assistant to mark/check it.\n6. Use learning_guidance when the student asks what to study next, how to plan revision, how to improve, or how to use learning/progress features, without asking for a topic explanation or a specific solution.\n7. Use out_of_scope for requests unrelated to learning support offered by Umwalimu AI, including unrelated personal, commercial, entertainment, travel, or transactional requests.\n8. Label the student's primary goal, not a single keyword. For example, 'explain why x=3' is explain_concept if the student asks for the reason, but 'solve 2x+4=10' is solve_problem.\n9. Keep message wording as supplied. Do not silently translate, correct spelling, expand SMS abbreviations, or normalize Kinyarwanda/mixed-language messages in the text column.\n10. If the intent is genuinely unclear or outside the defined learning functions, use out_of_scope rather than guessing.\n
## Where the messages come from

| Source | Rows |
|---|---:|
| rules | 0 |
| unmatched | 0 |
| local | 0 |
| people | 0 |
| written | 180 |

All 180 current rows are manually composed development examples. The `people`, `unmatched` and `local` sources must be added from genuine sources before submission. Collect at least 20 messages from people who were asked, anonymize them, and preserve the wording exactly as typed. Add the actual Portfolio Project 1 UNMATCHED log and Step 10 local phrasing.

## Quality check

Current draft checks:
- Total rows: 180
- Rows per label: 30 each
- Unknown labels: 0
- Duplicate messages after lowercase/punctuation normalization: 0
- Conflicting labels: 0
- Largest/smallest label ratio: 1.00
- Real-person messages: 0 (requirement not yet met)

The final six lines must be replaced with the actual output from Step 4 after all real source rows have been added and the notebook rerun.

## Split and baseline

144 training, 36 test. The provisional starter rules get **30 of 36** test messages right.\n\nThis is only a provisional baseline because the actual Portfolio Project 1 `RULES` table was not provided. Replace the notebook's provisional rules with the exact rules from Portfolio Project 1 and rerun Step 6 before submission.\n\nExamples the provisional rules misclassified:\n- `I keep forgetting what I study. What learning strategy can I try?` — expected `learning_guidance`, provisional rules predicted `out_of_scope`.\n- `What should I practise if I often make mistakes with fractions?` — expected `learning_guidance`, provisional rules predicted `out_of_scope`.\n- `What should I revise first for S2 maths?` — expected `learning_guidance`, provisional rules predicted `out_of_scope`.\n
## Entities

- `SUBJECT`: mathematics, maths, math, science, biology, physics, English, computer basics.
- `TOPIC`: algebra, fractions, geometry, photosynthesis, percentages, equations, area, perimeter, probability, water cycle, grammar, decimals, angles, and related learning topics.

Entity counts in the current draft, counting each message once per entity label:\n- `SUBJECT`: found in 21 messages.\n- `TOPIC`: found in 60 messages.\n
The notebook uses spaCy EntityRuler to calculate the final counts. Use the notebook's actual output in the submitted README.

## What is still weak

- `people`, `unmatched` and `local` source coverage is currently missing; these are required assignment evidence.
- The dataset is composed of manually written development examples and does not yet reflect actual student phrasing collected from the Umwalimu AI project.
- The proposed intent set must be checked against every intent actually implemented in Portfolio Project 1.
- The baseline rules are provisional, not the verified Portfolio Project 1 rules.
- Add and review genuine Kinyarwanda, mixed-language and SMS-style messages in every intent, keeping each original message unchanged.
- Review ambiguous cases with the labelling guideline, then rerun the quality report, split, baseline and entity counts.
