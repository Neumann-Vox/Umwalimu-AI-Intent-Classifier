# Umwalimu AI — Streamlit New Student Guide

This folder contains a deployment-compatible copy of the Streamlit app.

## Run from the repository root

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r streamlit/requirements.txt
streamlit run streamlit/app.py
```

## Streamlit Community Cloud

Choose this repository and branch `main`, then set the main file path to `streamlit/app.py`.

The root-level `app.py` is also supported. Both app files are kept aligned.

## Behaviour

The chatbot uses static response templates and transparent phrase matching. It covers first-day guidance, registration, student ID, facilities, rules, orientation, and student support. It does not call an LLM or require secrets.

Exact school-specific facts are not included. Students are directed to reception, administration, or student affairs for verified room locations, fees, dates, and policies. Add approved institution-specific knowledge before claiming that the bot knows a particular school's procedures.
