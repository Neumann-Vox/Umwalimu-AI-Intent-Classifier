from pathlib import Path
import re

import joblib
import streamlit as st

MODEL_PATH = Path(__file__).resolve().parent / "dataset" / "intent_classifier.joblib"
CONFIDENCE_THRESHOLD = 0.25

INTENT_NAMES = {
    "explain_concept": "Explain a concept",
    "solve_problem": "Solve a problem",
    "practice_request": "Practice questions",
    "check_answer": "Check an answer",
    "learning_guidance": "Study guidance",
    "out_of_scope": "Outside learning support",
}

INTENT_RESPONSES = {
    "explain_concept": (
        "I recognized this as a request to explain a concept. This demo can identify "
        "the request type, but it does not generate lesson explanations yet."
    ),
    "solve_problem": (
        "I recognized this as a problem-solving request. This demo can identify the "
        "request type, but it does not work through problems yet."
    ),
    "practice_request": (
        "I recognized this as a request for practice. This demo can identify the "
        "request type, but it does not generate exercises yet."
    ),
    "check_answer": (
        "I recognized this as an answer-checking request. This demo can identify the "
        "request type, but it cannot mark answers yet."
    ),
    "learning_guidance": (
        "I recognized this as a study-guidance request. This demo can identify the "
        "request type, but it does not create study plans yet."
    ),
    "out_of_scope": (
        "I can help identify requests about learning, such as explanations, worked "
        "problems, practice, answer checking, and study guidance."
    ),
}


def quick_response(message: str) -> str | None:
    normalized = re.sub(r"[^\\w\\s]", "", message.casefold())
    normalized = re.sub(r"\\s+", " ", normalized).strip()

    greetings = {
        "hi", "hello", "hey", "hello there", "hi there", "hey there",
        "good morning", "good afternoon", "good evening", "how are you",
    }
    thanks = {"thanks", "thank you", "thanks a lot", "thank you very much", "thx", "ty"}
    please = {"please", "pls", "plz"}

    if normalized in greetings:
        return (
            "Hello! What would you like to learn today? You can ask me to explain a "
            "concept, work through a problem, suggest practice, check an answer, or "
            "help plan your studies."
        )
    if normalized in thanks:
        return "You’re welcome! What learning topic would you like help with?"
    if normalized in please:
        return (
            "Of course. What would you like help with? Share a topic or question, "
            "and I’ll identify the kind of learning support you need."
        )
    return None


@st.cache_resource(show_spinner="Loading Umwalimu AI…")
def load_classifier():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. Run the classifier notebook first."
        )
    return joblib.load(MODEL_PATH)


st.set_page_config(
    page_title="Umwalimu AI",
    page_icon=":material/school:",
    layout="centered",
)

st.title("Umwalimu AI")
st.caption("Learning support intent demo")

with st.sidebar:
    st.subheader("About this demo")
    st.write(
        "This interface uses the trained classifier to recognize what kind of "
        "learning help a message asks for."
    )
    st.info(
        "It does not generate explanations, solve exercises, or mark answers yet.",
        title="Classifier only",
    )
    if st.button("Clear conversation", icon=":material/delete_sweep:"):
        st.session_state.messages = []
        st.rerun()

try:
    classifier = load_classifier()
except (FileNotFoundError, ModuleNotFoundError, ImportError, ValueError) as error:
    st.error(
        "The classifier could not be loaded. Install the versions in "
        "`requirements.txt` and confirm the model file exists at "
        "`dataset/intent_classifier.joblib`."
    )
    st.exception(error)
    st.stop()

st.session_state.setdefault("messages", [])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("intent"):
            intent_name = INTENT_NAMES.get(message["intent"], message["intent"])
            st.caption(f"Detected intent: {intent_name} · {message['confidence']:.0%} confidence")

if not st.session_state.messages:
    st.markdown("### What would you like help with?")
    suggestion = st.pills(
        "Try a message",
        [
            "Explain fractions in simple words",
            "Give me algebra practice questions",
            "Can you check my answer?",
        ],
        label_visibility="collapsed",
        key="suggested_prompt",
    )
else:
    suggestion = None

typed_prompt = st.chat_input("Ask about a lesson, a problem, or study practice")
prompt = typed_prompt or suggestion

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = quick_response(prompt)
    detected_intent = None
    confidence = None

    if response is None:
        probabilities = classifier.predict_proba([prompt])[0]
        top_index = int(probabilities.argmax())
        intent = str(classifier.classes_[top_index])
        confidence = float(probabilities[top_index])

        if confidence < CONFIDENCE_THRESHOLD:
            response = (
                "I’m not sure which learning request this is. Try asking for a concept "
                "explanation, a worked problem, practice questions, answer checking, or "
                "study guidance."
            )
        else:
            response = INTENT_RESPONSES.get(
                intent,
                "I recognized your request, but this demo does not have a response for that intent yet.",
            )
            detected_intent = intent

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "intent": detected_intent,
            "confidence": confidence,
        }
    )
    st.rerun()
