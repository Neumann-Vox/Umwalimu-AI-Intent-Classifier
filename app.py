import re

import streamlit as st

INTENT_RULES = {
    "greeting": ("hello", "hi", "hey", "good morning", "good afternoon", "good evening"),
    "bot_identity": ("who are you", "what is your name", "your name"),
    "capabilities": ("what can you do", "what can i ask", "how can you help"),
    "class_question": ("which class am i in", "what class am i in", "what is my class"),
    "ask_student_class": ("what class are you in", "which class are you in", "what grade are you in"),
    "share_class": ("i am in", "i'm in", "im in", "my class is", "i study in"),
    "ask_subject": ("which subject", "what subject", "subjects do you study"),
    "share_subject": ("i study", "i am studying", "i'm studying", "we are learning", "we're learning"),
    "topic_chat": ("learning about", "studying", "the topic is", "we learned", "we are learning"),
    "homework_chat": ("homework", "assignment", "schoolwork", "classwork"),
    "exam_chat": ("exam", "test", "quiz", "revision"),
    "timetable_chat": ("timetable", "schedule", "what time", "when does school", "school hours"),
    "wellbeing": ("sad", "stressed", "worried", "anxious", "nervous", "tired", "lonely", "upset", "overwhelmed"),
    "school_day": ("how was school", "my school day", "school today", "my teacher", "my classmates"),
    "gratitude": ("thanks", "thank you", "thx", "appreciate it"),
    "farewell": ("bye", "goodbye", "see you", "good night"),
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
    "computer studies": ("computer studies", "computing", "computer basics"),
    "social studies": ("social studies",),
    "kinyarwanda": ("kinyarwanda",),
}

TOPICS = (
    "fractions", "algebra", "geometry", "photosynthesis", "decimals",
    "equations", "grammar", "probability", "area", "perimeter",
    "water cycle", "angles",
)


def normalize(message: str) -> str:
    return re.sub(r"\s+", " ", message.casefold()).strip()


def contains_phrase(message: str, phrases) -> bool:
    return any(re.search(rf"\b{re.escape(phrase)}\b", message) for phrase in phrases)


def detect_intent(message: str) -> str:
    normalized = normalize(message)
    if find_class(message):
        return "share_class"
    if find_subject(message):
        return "share_subject"
    for intent, phrases in INTENT_RULES.items():
        if contains_phrase(normalized, phrases):
            return intent
    return "general_chat"


def find_class(message: str) -> str | None:
    match = re.search(
        r"\b(?:i am in|i'm in|im in|my class is|i study in|class|grade)\s*(s[1-6]|[1-9]|10|11|12)\b",
        message,
        re.I,
    )
    if not match:
        match = re.search(r"\b(s[1-6])\b", message, re.I)
    if not match:
        return None
    value = match.group(1).upper()
    return value if value.startswith("S") else f"Grade {value}"


def find_subject(message: str) -> str | None:
    normalized = normalize(message)
    for subject, names in SUBJECTS.items():
        if contains_phrase(normalized, names):
            return subject.title()
    return None


def find_topic(message: str) -> str | None:
    normalized = normalize(message)
    return next((topic for topic in TOPICS if contains_phrase(normalized, (topic,))), None)


def reply(intent: str, message: str) -> str:
    normalized = normalize(message)
    student_class = st.session_state.student_class
    subject = st.session_state.subject

    if intent == "greeting":
        if student_class:
            return f"Hello again, {student_class} student! What subject are you learning today?"
        return "Hello! I’m Umwalimu AI. Which class are you in? You can say “I’m in S2.”"
    if intent == "bot_identity":
        return "I’m Umwalimu AI, a friendly school chat companion. Which class are you in?"
    if intent == "capabilities":
        return "I can chat about your class, subjects, homework, exams, timetable, and how school is going. Tell me your class to get started."
    if intent == "class_question":
        if student_class:
            return f"You told me you’re in {student_class}. Did I remember correctly?"
        return "You haven’t told me your class yet. Which class are you in?"
    if intent == "ask_student_class":
        return "I’m a chatbot, so I don’t attend a class. I’d like to hear about yours! Which class are you in?"
    if intent == "share_class":
        return f"Nice! I’ll remember {student_class} during this chat. What subject are you studying?"
    if intent == "ask_subject":
        if subject:
            return f"You said you’re studying {subject}. What are you learning in that subject?"
        return f"What subject are you studying in {student_class or 'your class'}? You can say mathematics, science, English, or another subject."
    if intent == "share_subject":
        if student_class:
            return f"Got it — {subject} in {student_class}. What topic are you learning about?"
        return f"Great, let’s chat about {subject}. Which class are you in?"
    if intent == "topic_chat":
        topic = find_topic(message)
        if topic:
            return f"{topic.title()} — interesting! What part of it is your class discussing?"
        return f"What topic are you learning in {subject or 'class'}?"
    if intent == "homework_chat":
        return f"Let’s talk about your homework. Which subject is it for{f' in {student_class}' if student_class else ''}?"
    if intent == "exam_chat":
        return "Exams can feel like a lot. Which subject are you preparing for, and when is the exam?"
    if intent == "timetable_chat":
        return "I don’t know your school’s timetable. What time does your class start, or what part of your school day are you asking about?"
    if intent == "wellbeing":
        return "I’m sorry you’re feeling that way. Do you want to tell me what happened at school? If you feel unsafe or overwhelmed, please talk with a trusted adult or teacher."
    if intent == "school_day":
        return "How did your school day go? What was one thing you liked or found difficult?"
    if intent == "gratitude":
        return "You’re welcome! What else would you like to chat about at school?"
    if intent == "farewell":
        return "Goodbye! I enjoyed chatting with you. Good luck at school!"
    if student_class is None:
        return "I’m here to chat about student life and school. First, which class are you in?"
    if subject is None:
        return f"Thanks, {student_class}! What subject are you learning today?"
    return f"Got it — {subject} in {student_class}. Tell me what’s happening in class."


st.set_page_config(page_title="Umwalimu AI", page_icon=":material/school:", layout="centered")
st.title("Umwalimu AI")
st.caption("A friendly school conversation")

with st.sidebar:
    st.subheader("Your chat")
    st.write("I can chat about your class, subjects, homework, exams, timetable, and school day.")
    st.caption("I remember your class and subject until you start a new chat.")
    if st.button("Start a new chat", icon=":material/chat:"):
        st.session_state.messages = []
        st.session_state.student_class = None
        st.session_state.subject = None
        st.rerun()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("student_class", None)
st.session_state.setdefault("subject", None)

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

if not st.session_state.messages:
    st.markdown("### Say hello to start")
    st.caption("Try: “Hello” · “I’m in S2” · “I study mathematics” · “I have exams soon”")

prompt = st.chat_input("Say hello or tell me what is happening at school")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    student_class = find_class(prompt)
    subject = find_subject(prompt)
    if student_class:
        st.session_state.student_class = student_class
    if subject:
        st.session_state.subject = subject

    intent = detect_intent(prompt)
    response = reply(intent, prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
