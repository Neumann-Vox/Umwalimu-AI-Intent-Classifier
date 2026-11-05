# Umwalimu AI — Student Conversation Chatbot

Umwalimu AI is a simple rule-based chatbot for student conversations. It remembers a student's class and subject during the chat and responds to common school-related messages.

## Conversation intents

The chatbot recognizes 18 conversation intents: greetings, bot identity, capabilities, asking or sharing a class, asking or sharing a subject, asking about a topic, discussing a topic, homework, exams, timetable, wellbeing, school day, school events, thanks, and goodbye. If a message does not match, it asks a friendly follow-up.

This version does not solve exercises, generate quizzes, or mark answers. Replies come from app.py; no AI service or API key is needed.

## Run on Windows

Open Command Prompt and run:

    git clone -b feature/student-conversation-intents https://github.com/Neumann-Vox/Umwalimu-AI-Intent-Classifier.git
    cd Umwalimu-AI-Intent-Classifier
    py -3.11 -m venv .venv
    .venv\Scripts\activate.bat
    python -m pip install -r requirements.txt
    streamlit run app.py

Open the local address Streamlit prints, usually http://localhost:8501.

## Example conversation

- Student: “Hello”
- Umwalimu AI: “Which class are you in?”
- Student: “I’m in S2”
- Umwalimu AI: “What subject are you studying?”
- Student: “Mathematics”
- Umwalimu AI: “What topic are you learning about?”

The chatbot remembers the class and subject until **Start a new chat** is selected.

## Assignment materials

The classifier assignment work remains under dataset/: the notebook, original labeled dataset, trained model, and technical report. The live chatbot uses its own conversational rules. The technical report explains the classifier dataset, results, and remaining source-evidence requirements.
