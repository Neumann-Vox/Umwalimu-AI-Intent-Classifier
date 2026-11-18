from datetime import datetime, timezone
from pathlib import Path
import uuid

import joblib
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "intent_classifier.joblib"
THRESHOLD = 0.25

INTENT_HELP = {
    "explain_concept": (
        "I can explain that concept step by step. Please send the exact topic and your class "
        "(for example, S2), so I can choose an appropriate level."
    ),
    "solve_problem": (
        "Let's work through it together. Send the complete question, the subject, and any "
        "steps you have already tried."
    ),
    "practice_request": (
        "I can help you practise. Tell me the topic, your class, and how many questions you want."
    ),
    "check_answer": (
        "I can help check your work. Send the original question, your answer, and your working "
        "so I can explain any correction."
    ),
    "learning_guidance": (
        "Let's make a realistic study plan. Tell me your class, the subjects you are studying, "
        "and when your next test or examination is."
    ),
    "out_of_scope": (
        "I am designed to support school learning. Ask me about a lesson, exercise, practice "
        "questions, checking an answer, or planning your studies."
    ),
}

# Short, general learning notes for the optional FAQ retriever.
# Add passages from approved course materials here when you have permission to use them.
FAQ = [
    ("Photosynthesis",
     "Photosynthesis is the process by which green plants use light energy to make food "
     "from water and carbon dioxide. Oxygen is released during the process."),
    ("Fractions",
     "A fraction represents part of a whole. The numerator is the top number and tells how "
     "many parts are being considered. The denominator is the bottom number and tells how "
     "many equal parts make the whole. For example, 3/4 means three out of four equal parts."),
    ("The water cycle",
     "The water cycle describes the continuous movement of water. Evaporation changes liquid "
     "water into water vapour, condensation forms clouds, precipitation brings water back as "
     "rain or other forms, and collection gathers water in rivers, lakes and oceans."),
    ("Area and perimeter",
     "Area measures the surface inside a two-dimensional shape and is expressed in square "
     "units. Perimeter is the total distance around the outside of a shape and is expressed "
     "in linear units. For a rectangle, area = length × width and perimeter = 2 × (length + width)."),
    ("Variables",
     "A variable is a symbol, often a letter such as x, that represents a number whose value "
     "may be unknown or may change. In 2x + 5 = 15, x is the variable."),
    ("Solving a simple equation",
     "To solve 2x + 5 = 15, subtract 5 from both sides: 2x = 10. Divide both sides by 2: "
     "x = 5. Check: 2(5) + 5 = 15, so the answer is correct."),
    ("The three states of matter",
     "The three common states of matter are solid, liquid and gas. A solid has a fixed shape "
     "and volume. A liquid has a fixed volume but takes the shape of its container. A gas "
     "spreads out to fill its container."),
    ("The human heart",
     "The human heart is a muscular organ that pumps blood around the body. The right side "
     "sends blood to the lungs to receive oxygen, while the left side pumps oxygen-rich blood "
     "to the rest of the body."),
    ("Computer hardware and software",
     "Hardware refers to the physical parts of a computer, such as the keyboard, monitor, "
     "processor and memory. Software is the set of programs and instructions that tell the "
     "hardware what to do."),
    ("Simple interest",
     "Simple interest is calculated on the original amount of money. The formula is "
     "I = (P × R × T) / 100, where P is the principal, R is the annual interest rate "
     "as a percentage, and T is time in years. For example, 10,000 RWF at 5% for 2 years "
     "earns 1,000 RWF interest."),
]

@st.cache_resource(show_spinner="Loading the Part 1 intent classifier…")
def load_classifier():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "intent_classifier.joblib must be in the same folder as streamlit/app.py."
        )
    return joblib.load(MODEL_PATH)

@st.cache_resource
def build_retriever():
    vectorizer = TfidfVectorizer(stop_words="english")
    documents = [f"{topic}. {passage}" for topic, passage in FAQ]
    matrix = vectorizer.fit_transform(documents)
    return vectorizer, matrix

def get_secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None

def classify_message(classifier, message):
    probabilities = classifier.predict_proba([message])[0]
    best_index = int(probabilities.argmax())
    return str(classifier.classes_[best_index]), float(probabilities[best_index])

def retrieve_faq(message):
    vectorizer, matrix = build_retriever()
    question_vector = vectorizer.transform([message])
    scores = cosine_similarity(question_vector, matrix)[0]
    best_index = int(scores.argmax())
    return float(scores[best_index]), FAQ[best_index]

def ask_openrouter(message, intent, student_class, faq_passage=None):
    api_key = get_secret("OPENROUTER_API_KEY")
    if not api_key:
        return None

    facts = ""
    if faq_passage:
        facts = (
            "\nUse this relevant learning note when it helps; do not claim it is an official "
            f"Rwandan curriculum quotation:\n{faq_passage[0]}: {faq_passage[1]}"
        )

    system_message = (
        "You are Umwalimu AI, a patient educational learning assistant for students. "
        "Answer clearly, accurately, and at the student's level. Use short steps and a simple "
        "example where useful. If the student asks to solve a problem, show the reasoning, not "
        "only the final answer. If checking an answer, ask for the original question and working "
        "when they are missing. Do not invent official Rwanda curriculum requirements, textbook "
        "references, examination answers, or sources. If uncertain, say so and ask for the "
        "relevant lesson material. Keep the answer focused on the student's learning request. "
        f"Detected intent: {intent}. Student class: {student_class or 'not provided'}. "
        + facts
    )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://umwalimu-ai.streamlit.app",
                "X-Title": "Umwalimu AI Student Learning Assistant",
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message},
                ],
            },
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return answer.strip() if answer else None
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return None

def make_reply(classifier, message, student_class):
    intent, confidence = classify_message(classifier, message)
    if confidence < THRESHOLD:
        intent = "out_of_scope"

    # Try a relevant FAQ passage first. The similarity threshold is deliberately conservative.
    faq_score, faq_item = retrieve_faq(message)
    faq_passage = faq_item if faq_score >= 0.18 else None

    generated = ask_openrouter(message, intent, student_class, faq_passage)
    if generated:
        return generated, intent, confidence, "llm"

    # Use the built-in lesson library for relevant questions even when no API key
    # is configured. This makes the demo useful offline and keeps answers predictable.
    if faq_passage and faq_score >= 0.18:
        return faq_passage[1], intent, confidence, "lesson library"

    return INTENT_HELP[intent], intent, confidence, "classifier"

def log_to_sheet(row):
    log_url = get_secret("LOG_URL")
    if not log_url:
        return False
    try:
        response = requests.post(log_url, json=row, timeout=10)
        return response.ok and response.text.strip().lower() == "ok"
    except requests.RequestException:
        return False

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

st.set_page_config(page_title="Umwalimu AI", page_icon="📚", layout="centered")
st.title("📚 Umwalimu AI")
st.caption(
    "A student learning conversation assistant. Ask for an explanation, a worked problem, "
    "practice, answer checking, or study guidance."
)

with st.expander("See example questions you can ask"):
    st.markdown(
        """
        - **Biology:** What is photosynthesis?
        - **Biology:** Explain the water cycle.
        - **Science:** What are the three states of matter?
        - **Human biology:** What does the heart do?
        - **Mathematics:** What is a fraction?
        - **Mathematics:** How do I solve 2x + 5 = 15?
        - **Mathematics:** What is the difference between area and perimeter?
        - **Mathematics:** What is a variable?
        - **ICT:** What is the difference between computer hardware and software?
        - **Business mathematics:** How do I calculate simple interest?
        """
    )

with st.sidebar:
    st.subheader("About this chatbot")
    st.write(
        "The Part 1 machine-learning classifier identifies six learning intents. "
        "The chatbot then selects a response or, when configured, asks an optional language model."
    )
    st.caption(f"Classifier confidence threshold: {THRESHOLD:.2f}")
    if st.button("Start a new chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.student_class = ""
        st.session_state.user_code = uuid.uuid4().hex[:10]
        st.session_state.feedback_logged = set()
        st.rerun()

try:
    classifier = load_classifier()
except Exception as error:
    st.error("The Part 1 model could not be loaded. Check the model file and package versions.")
    st.exception(error)
    st.stop()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("student_class", "")
st.session_state.setdefault("user_code", uuid.uuid4().hex[:10])
st.session_state.setdefault("feedback_logged", set())

if not st.session_state.messages:
    st.info(
        "Try: “Explain photosynthesis”, “Help me solve 2x + 5 = 15”, "
        "“Give me practice questions”, or “Help me plan my revision”."
    )

for index, item in enumerate(st.session_state.messages):
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item["role"] == "assistant":
            st.caption(
                f"Intent: {item['intent']} · Confidence: {item['confidence']:.2f} "
                f"· Answered by: {item['answered_by']}"
            )
            feedback_key = f"feedback_{item['turn']}"
            feedback_value = st.feedback("thumbs", key=feedback_key)
            if feedback_value is not None and item["turn"] not in st.session_state.feedback_logged:
                feedback_row = {
                    "time": utc_now(),
                    "user": st.session_state.user_code,
                    "turn": item["turn"],
                    "feedback": "👍" if feedback_value == 1 else "👎",
                }
                if log_to_sheet(feedback_row):
                    st.session_state.feedback_logged.add(item["turn"])

prompt = st.chat_input("Write your learning question…")
if prompt:
    cleaned = prompt.strip()
    if not cleaned:
        st.warning("Please type a question or message.")
        st.stop()
    if len(cleaned) > 1500:
        st.warning("Please keep each message under 1,500 characters.")
        st.stop()

    st.session_state.messages.append({
        "role": "user",
        "content": cleaned,
        "turn": len(st.session_state.messages) // 2 + 1,
    })

    # Remember a class only when the student explicitly provides it.
    import re
    class_match = re.search(
        r"\b(?:i am in|i'm in|im in|my class is|class)\s*(nursery|p[1-6]|s[1-6])\b",
        cleaned,
        re.IGNORECASE,
    )
    if class_match:
        st.session_state.student_class = class_match.group(1).upper()

    answer, intent, confidence, answered_by = make_reply(
        classifier, cleaned, st.session_state.student_class
    )
    turn = (len(st.session_state.messages) + 1) // 2
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "turn": turn,
        "intent": intent,
        "confidence": confidence,
        "answered_by": answered_by,
    })

    log_row = {
        "time": utc_now(),
        "user": st.session_state.user_code,
        "turn": turn,
        "message": cleaned,
        "intent": intent,
        "confidence": round(confidence, 3),
        "answered_by": answered_by,
        "reply": answer,
        "feedback": "",
    }
    if not log_to_sheet(log_row) and get_secret("LOG_URL"):
        st.warning("This turn could not be saved to the Google Sheet.")
    st.rerun()

if not get_secret("LOG_URL"):
    st.caption("Conversation logging is not configured. Add LOG_URL in Streamlit Secrets to enable it.")
if not get_secret("OPENROUTER_API_KEY"):
    st.caption(
        "Optional AI answer generation is not configured. Add OPENROUTER_API_KEY in Streamlit "
        "Secrets to enable generated educational explanations."
    )
