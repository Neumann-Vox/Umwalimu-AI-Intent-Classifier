# Umwalimu AI — Portfolio Project 2 Part 2 (Streamlit)

This folder contains the Streamlit version of the chatbot submission. It loads the saved
Part 1 scikit-learn classifier from `intent_classifier.joblib` and uses the selected
confidence threshold of **0.25**.

## Files

- `app.py` — Streamlit chat interface, classifier integration, response routing, optional
  FAQ retrieval, optional language-model support, and conversation/feedback logging.
- `requirements.txt` — runtime packages. The scikit-learn version is pinned to 1.8.0,
  the version recorded in the Part 1 model notes.
- `intent_classifier.joblib` — the trained Part 1 model. Keep it beside `app.py`.

## Run locally (Windows)

From the repository root:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r streamlit/requirements.txt
streamlit run streamlit/app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud and create an app.
3. Select this repository, branch `main`, and main file path `streamlit/app.py`.
4. Deploy.

## Optional Google Sheets logging (criterion 3.6)

The lecturer's setup guide describes the private Google Sheet and Apps Script deployment.

1. Create a private Google Sheet.
2. Open Extensions → Apps Script and paste the lecturer-provided `apps_script.gs` code.
   Save and deploy it as a Web app. Set “Execute as” to Me and access to Anyone, as the
   lecturer's guide specifies.
3. Copy the deployed Web app URL ending in `/exec`.
4. In Streamlit Community Cloud, open the app's Settings → Secrets and add:

```toml
LOG_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
```

5. Save and test a chat message. A row should appear in the Sheet. Feedback is logged
   separately when a student selects a thumbs-up or thumbs-down rating.

Do not commit the Sheet URL or the Apps Script file to this repository.

## Optional language-model answers

Add your own OpenRouter key in Streamlit Secrets:

```toml
OPENROUTER_API_KEY = "YOUR_PRIVATE_KEY"
```

This key is optional. Never put it in `app.py`, a notebook, README, screenshot, or GitHub.
Without it, the app still loads the classifier and returns its built-in learning guidance
and relevant FAQ passages.

## Classifier intents

- `explain_concept`
- `solve_problem`
- `practice_request`
- `check_answer`
- `learning_guidance`
- `out_of_scope`

The model's confidence is compared with the Part 1 threshold of 0.25. The FAQ notes are
general examples; replace or expand them with permitted, verified learning materials.
