# Umwalimu AI — Student Chatbot

Umwalimu AI is a small school conversation chatbot built for the Assignment 8 intent-classification project. It greets students, asks what class and subject they are studying, remembers those answers during the chat, and asks friendly follow-up questions.

The saved machine-learning classifier identifies broad message intents. Simple conversation rules produce the replies. The chatbot does not solve problems or generate unrestricted answers.

## Run on Windows

Open Command Prompt and run:

```cmd
git clone -b feature/streamlit-chat-interface-ready https://github.com/Neumann-Vox/Umwalimu-AI-Intent-Classifier.git
cd Umwalimu-AI-Intent-Classifier
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local address Streamlit prints, usually http://localhost:8501.

## Try a conversation

- Student: “Hello”
- Umwalimu AI: “Which class are you in?”
- Student: “I’m in S2”
- Umwalimu AI: “What subject are you learning?”
- Student: “Mathematics”
- Umwalimu AI: “What topic is your class learning about?”

It also responds to thanks, goodbyes, and common school-related requests. Use **Start a new chat** to clear the conversation and saved class/subject.

## Assignment files

- `dataset/Portfolio_Project_2_Part_1_Classifier.ipynb`: dataset audit, baseline, model training, evaluation, and saved classifier.
- `dataset/intents.csv`: labelled and split messages used by the notebook.
- `dataset/intent_classifier.joblib`: trained classifier used by the chat interface.
- `dataset/README.md`: model results, data provenance, limitations, and outstanding assignment evidence.

The notebook and dataset are retained because they are the core classifier assignment work. The dataset README records evidence that still needs to be supplied before claiming the assignment is fully complete, including genuine participant messages and original project materials. Do not present invented messages as real participant data.

## Intent labels

`explain_concept`, `solve_problem`, `practice_request`, `check_answer`, `learning_guidance`, and `out_of_scope`.
