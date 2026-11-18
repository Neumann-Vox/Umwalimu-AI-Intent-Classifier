# Umwalimu AI — New Student Guide

Umwalimu AI is a Streamlit chatbot that gives new students simple, predictable guidance about getting started at school.

## Current scope

- First-day guidance
- Registration and admissions process
- Student ID guidance
- Finding school facilities
- Understanding school rules
- Orientation information
- Student support and safe escalation

This version uses deterministic intent routing and static response templates. It does not require an API key, an external language model, or a downloaded model file.

## Start a conversation

1. Student: **Hello**
2. Umwalimu AI: welcomes the student and asks what they need help with.
3. Student can then ask, for example:
   - I am new. Where should I go first?
   - How do I complete my registration?
   - How can I get my student ID?
   - Where is the library?
   - What are the school rules?
   - When is student orientation?
   - I need help with a personal problem.

## Run locally (Windows CMD)

```cmd
git clone https://github.com/Neumann-Vox/Umwalimu-AI-Intent-Classifier.git
cd Umwalimu-AI-Intent-Classifier
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new app in Streamlit Community Cloud.
2. Choose repository `Neumann-Vox/Umwalimu-AI-Intent-Classifier`.
3. Select branch `main`.
4. Set the main file path to **app.py**.
5. Deploy.

The duplicate `streamlit/app.py` is kept aligned for deployments that use that path; if selecting it, set the main file path to `streamlit/app.py`.

## Important data limitation

The repository does not contain verified information about a particular school's offices, room numbers, facility locations, opening hours, registration deadlines, fees, or orientation dates. The chatbot gives safe general guidance and tells students to confirm exact information with reception, administration, or student affairs. Do not present demo content as official school policy.

## Intent dataset and notebook

- `intents.csv` and `dataset/intents.csv`: curated demonstration examples for the new-student intents.
- `dataset/Portfolio_Project_2_Part_1_Classifier.ipynb`: dataset audit, intent distribution, TF-IDF + Logistic Regression baseline, evaluation, and model export.
- `dataset/intent_classifier.joblib`: legacy/previous model artifact; the static Streamlit application does not load it.

The examples are not real student interviews. Collect consent-based, anonymised student questions and verify institutional knowledge before making performance or school-specific accuracy claims.
