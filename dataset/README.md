# New Student Guide — Intent Dataset and Notebook

This directory contains the intent-classification experiment for the current Umwalimu AI New Student Guide.

## Dataset schema

| Column | Meaning |
|---|---|
| `text` | Example student message |
| `intent` | Target intent label |
| `source` | `curated_demo` means manually written demonstration phrase |
| `split` | Predefined `train` or `test` partition |

## Current intents

- `greeting`
- `first_day_guidance`
- `registration_help`
- `student_id_help`
- `facility_location`
- `school_rules`
- `orientation_info`
- `student_support`
- `general_school_help`
- `out_of_scope`

The CSV currently has eight curated example phrases per intent. These are demonstration examples, not messages collected from real students. Do not claim the dataset represents student populations or has production-level accuracy.

## Notebook

Run `Portfolio_Project_2_Part_1_Classifier.ipynb` from the repository root. It audits the CSV, plots the class distribution, trains a TF-IDF + Logistic Regression baseline, reports held-out metrics, and saves an experimental `intent_classifier.joblib`.

The deployed Streamlit app currently uses transparent keyword rules and static answer templates, not the experimental model. This is intentional: the first deployment should be predictable and work without an API key or model artifact.

## Before a real school deployment

1. Collect anonymised, consent-based example questions from students.
2. Review labels with school staff.
3. Add verified school-specific information only after approval.
4. Test intent confusion, unknown questions, and sensitive-support escalation.
5. Never invent room numbers, fees, schedules, policies, or contact details.
