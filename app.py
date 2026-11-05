from pathlib import Path
import re

import joblib
import streamlit as st

MODEL_PATH = Path(__file__).resolve().parent / "dataset" / "intent_classifier.joblib"
CONFIDENCE_THRESHOLD = 0.25

INTENT_LABELS = {
    "explain_concept": "concept question",
    "solve_problem": "problem discussion",
    "practice_request": "practice request",
    "check_answer": "answer discussion",
    "learning_guidance": "study guidance",
    "out_of_scope": "outside school support",
}

SUBJECTS = {
    "mathematics": ("mathematics", "math", "maths"),
    "science": ("science",),
    "biology": ("biology",),
    "physics": ("physics",),
    "chemistry": ("chemistry",),
    "english": ("english",),
    "history": ("history",),
    "geography": ("geography",),
    "computer studies": ("computer studies", "computer basics", "computing"),
}


def clean(message: str) -> str:
    return re.sub(r"\s+", " ", message.casefold()).strip()


def find_class(message: str) -> str | None:
    match = re.search(r"\b(?:i am in|i'm in|im in|my class is|class|grade)\s*(s[1-6]|[1-9]|10|11|12)\b", message, re.I)
    if not match:
        match = re.search(r"\b(s[1-6])\b", message, re.I)
    if not match:
        return None
    value = match.group(1).upper()
    return value if value.startswith("S") else f"Grade {value}"


def find_subject(message: str) -> str | None:
    lowered = clean(message)
    for subject, names in SUBJECTS.items():
        if any(re.search(rf"\b{re.escape(name)}\b", lowered) for name in names):
            return subject.title()
    return None


def quick_reply(message: str) -> str | None:
    normalized = re.sub(r"[^\w\s']", "", clean(message))
    if normalized in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
        return "Hello! I’m Umwalimu AI. Which class are you in? You can say something like “I’m in S2.”"
    if normalized in {"thanks", "thank you", "thank you so much", "thx"}:
        return "You’re welcome! What subject are you learning today?"
    if normalized in {"bye", "goodbye", "see you", "good night"}:
        return "Goodbye! Good luck with your studies. Come back whenever you want to chat."
    if normalized in {"how are you", "how are you doing"}:
        return "I’m doing well and ready to chat about school. How are you? Which class are you in?"
    if normalized in {"what can you do", "what can i ask", "help"}:
        return "I can chat with you about your class, subjects, and what you’re learning. Tell me your class first, then we can talk about a subject or topic."
    return None


def make_reply(message: str, detected_intent: str | None) -> str:
    lowered = clean(message)

    if any(phrase in lowered for phrase in ("what class are you", "which class are you", "are you a student")):
        return "I’m a chatbot, so I don’t attend a class. I’m here to chat with you about yours! Which class are you in?"

    if "which class am i" in lowered or "what class am i" in lowered:
        if st.session_state.student_class:
            return f"You told me you’re in {st.session_state.student_class}. Did I remember that correctly?"
        return "You haven’t told me your class yet. Which class are you in?"

    if st.session_state.student_class is None:
        return "Nice to meet you! Which class are you in? For example, you can say “I’m in S2.”"

    if st.session_state.subject is None:
        return f"Thanks, {st.session_state.student_class}! What subject are you studying today?"

    subject = st.session_state.subject
    school_context = f"your {st.session_state.student_class} {subject} class"
    if detected_intent == "learning_guidance":
        return f"What would you like to work toward in {school_context?} Tell me your study goal, and we can talk about a simple next step."
    if detected_intent == "out_of_scope":
        return f"I’m here to chat about school and learning. What’s happening in {school_context}?"
    if detected_intent:
        label = INTENT_LABELS.get(detected_intent, "school topic")
        return f"Okay, that sounds like a {label} for {school_context}. What topic is your class talking about?"
    return f"Got it — {subject} in {st.session_state.student_class}. What topic is your class learning about?"


@st.cache_resource(show_spinner="Starting Umwalimu AI…")
def load_classifier():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Classifier file not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="Umwalimu AI", page_icon=":material/school:", layout="centered")
st.title("Umwalimu AI")
st.caption("A friendly school conversation")

with st.sidebar:
    st.subheader("Your chat")
    st.write("Tell Umwalimu AI your class and subject. It will remember them during this conversation.")
    st.caption("This assignment demo uses a trained intent classifier and simple conversation rules.")
    if st.button("Start a new chat", icon=":material/chat:"):
        st.session_state.messages = []
        st.session_state.student_class = None
        st.session_state.subject = None
        st.rerun()

try:
    classifier = load_classifier()
except (FileNotFoundError, ModuleNotFoundError, ImportError, ValueError) as error:
    st.error("The chatbot could not load its saved classifier. Install requirements.txt and check dataset/intent_classifier.joblib.")
    st.exception(error)
    st.stop()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("student_class", None)
st.session_state.setdefault("subject", None)

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

if not st.session_state.messages:
    st.markdown("### Start with a greeting")
    st.caption("Examples: “Hello” · “I’m in S2” · “I study mathematics”")

prompt = st.chat_input("Say hello or tell me about your class")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    student_class = find_class(prompt)
    subject = find_subject(prompt)
    if student_class:
        st.session_state.student_class = student_class
    if subject:
        st.session_state.subject = subject

    response = quick_reply(prompt)
    if response is None:
        lowered = clean(prompt)
        if any(word in lowered for word in ("my class", "which class", "what class")) and not student_class:
            if st.session_state.student_class:
                response = f"You told me you’re in {st.session_state.student_class}. What subject are you learning?"
            else:
                response = "Which class are you in? You can say something like “I’m in S2.”"
        elif any(word in lowered for word in ("what subject", "which subject", "what are we learning", "what am i studying")):
            if st.session_state.subject:
                response = f"You told me you’re studying {st.session_state.subject}. What topic are you covering?"
            else:
                response = f"What subject are you studying in {st.session_state.student_class or 'your class'}?"
        elif student_class and subject:
            response = f"Nice! I’ll remember {student_class} and {subject} for this chat. What topic are you learning?"
        elif student_class:
            response = f"Nice to meet you, {student_class} student! What subject are you learning?"
        elif subject:
            if st.session_state.student_class:
                response = f"Got it — {subject} in {st.session_state.student_class}. What topic are you learning?"
            else:
                response = f"Great, let’s talk about {subject}. Which class are you in?"
        else:
            probabilities = classifier.predict_proba([prompt])[0]
            best_index = int(probabilities.argmax())
            intent = str(classifier.classes_[best_index])
            confidence = float(probabilities[best_index])
            if confidence < CONFIDENCE_THRESHOLD:
                intent = None
            response = make_reply(prompt, intent)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
