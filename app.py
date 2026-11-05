import ast
import operator
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

TOPIC_EXPLANATIONS = {
    "fraction": "A fraction shows equal parts of a whole. In 3/4, the bottom number (4) tells how many equal parts make the whole; the top number (3) tells how many parts we mean.",
    "photosynthesis": "Photosynthesis is how green plants use light energy to make food. They take in water and carbon dioxide, and release oxygen.",
    "algebra": "Algebra uses letters such as x to stand for numbers we do not know yet. We use the same rules as arithmetic to find those numbers.",
    "decimal": "A decimal uses place value to show parts of one. For example, 0.5 means five tenths, which is the same as one half.",
    "perimeter": "Perimeter is the distance around the outside of a flat shape. Add the lengths of all its sides to find it.",
    "area": "Area measures the surface inside a flat shape. For a rectangle, multiply its length by its width.",
    "variable": "A variable is a letter or symbol that represents a number. In x + 3 = 8, x is the variable.",
    "equation": "An equation says two expressions have the same value. To solve it, do the same operation to both sides until the unknown is by itself.",
    "probability": "Probability describes how likely an event is. It ranges from 0 (impossible) to 1 (certain); for equally likely outcomes, divide favorable outcomes by all outcomes.",
}

PRACTICE_QUESTIONS = {
    "fraction": "1) What is 1/2 + 1/4?\n2) Which is larger: 2/3 or 3/5?\n3) Find 3/4 of 20.",
    "algebra": "1) Solve x + 5 = 12.\n2) Solve 3x = 21.\n3) Simplify 2x + 4x.",
    "decimal": "1) Calculate 0.4 + 0.35.\n2) Write 3/10 as a decimal.\n3) What is 10% of 80?",
    "photosynthesis": "1) What energy source do plants use?\n2) Name two things plants take in during photosynthesis.\n3) Which gas do plants release?",
    "equation": "1) Solve x - 4 = 9.\n2) Solve 2x = 18.\n3) Solve x/3 = 5.",
}

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def topic_in(message: str, topics) -> str | None:
    lowered = message.casefold()
    for topic in topics:
        if topic in lowered or (topic == "fraction" and "fractions" in lowered) or (topic == "decimal" and "decimals" in lowered):
            return topic
    return None


def quick_response(message: str) -> str | None:
    normalized = re.sub(r"[^\w\s]", "", message.casefold())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if normalized in {"hi", "hello", "hey", "hello there", "hi there", "hey there", "good morning", "good afternoon", "good evening", "how are you"}:
        return "Hello! What would you like to learn today? Ask me to explain a topic, solve a short arithmetic problem, make practice questions, check a calculation, or plan your study."
    if normalized in {"thanks", "thank you", "thanks a lot", "thank you very much", "thx", "ty"}:
        return "You’re welcome! What would you like to learn next?"
    if normalized in {"please", "pls", "plz"}:
        return "Of course. Tell me the topic or paste the question you want help with."
    return None


def evaluate_arithmetic(node):
    if isinstance(node, ast.Expression):
        return evaluate_arithmetic(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return node.value
    if isinstance(node, ast.BinOp):
        left = evaluate_arithmetic(node.left)
        right = evaluate_arithmetic(node.right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > 6:
                raise ValueError("Power is too large")
            return left ** right
        if type(node.op) in _BINARY_OPERATORS:
            return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](evaluate_arithmetic(node.operand))
    raise ValueError("Unsupported arithmetic expression")


def arithmetic_value(expression: str):
    return evaluate_arithmetic(ast.parse(expression, mode="eval"))


def rule_based_reply(intent: str, message: str) -> str:
    topic = topic_in(message, TOPIC_EXPLANATIONS)
    if intent == "explain_concept":
        if topic:
            return TOPIC_EXPLANATIONS[topic] + "\n\nWant a short example to try?"
        return "Which topic should I explain? For example, ask: Explain fractions in simple words. I currently have short explanations for fractions, photosynthesis, algebra, decimals, perimeter, area, variables, equations, and probability."
    if intent == "solve_problem":
        match = re.search(r"(?<![\w.])([0-9.()\s+*/%\-]{3,})", message)
        if match:
            expression = match.group(1).strip().rstrip(" .?")
            try:
                if not expression or not re.search(r"\d", expression) or len(expression) > 60:
                    raise ValueError("No short arithmetic expression")
                answer = arithmetic_value(expression)
                return f"Let’s work it out: {expression} = {answer:g}. I followed order of operations. If you meant a different expression, paste it by itself."
            except (SyntaxError, ValueError, ZeroDivisionError, TypeError, OverflowError):
                pass
        return "I can work through short arithmetic expressions in this demo. Paste one clearly, such as: solve 3/4 + 1/2. For equations or longer word problems, I can identify the request but need a fuller solver."
    if intent == "practice_request":
        if topic and topic in PRACTICE_QUESTIONS:
            return f"Here are three practice questions on {topic}:\n\n{PRACTICE_QUESTIONS[topic]}\n\nSend your answers and I’ll try to check a simple calculation."
        return "Try these: 1) Solve x + 6 = 14. 2) Calculate 3/4 + 1/2. 3) Find the area of a rectangle that is 5 cm by 3 cm. Tell me a topic for a more focused set."
    if intent == "check_answer":
        equality = re.search(r"([0-9.()\s+*/%\-]{1,60})=\s*([0-9.()\s+*/%\-]{1,30})", message)
        if equality:
            try:
                left = arithmetic_value(equality.group(1).strip())
                right = arithmetic_value(equality.group(2).strip())
                if abs(left - right) < 1e-9:
                    return f"That calculation is correct: {equality.group(1).strip()} equals {right:g}."
                return f"That calculation does not match: the left side is {left:g}, while the answer you wrote is {right:g}. Check the operation signs and order."
            except (SyntaxError, ValueError, ZeroDivisionError, TypeError, OverflowError):
                pass
        return "Paste the calculation and your answer in one message, for example: 2 + 3 * 4 = 20. I can check short arithmetic calculations; other answer types need a subject-specific checker."
    if intent == "learning_guidance":
        return "Here’s a simple study routine: 1) Pick one small topic. 2) Review an example for 10 minutes. 3) Try a few questions without looking. 4) Check mistakes and revisit them tomorrow. Tell me your subject and available study time for a more focused plan."
    return "I’m focused on learning support. Try asking for a concept explanation, a worked arithmetic problem, practice questions, answer checking, or study guidance."


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
st.caption("Learning support chatbot · ML intent classifier + rule-based replies")

with st.sidebar:
    st.subheader("About this demo")
    st.write(
        "A trained machine-learning model classifies the message intent. "
        "A small rule-based response layer then provides greetings, selected topic "
        "explanations, arithmetic checks, practice questions, and study guidance."
    )
    st.info(
        "Replies are limited to the built-in rules and examples. This is not a generative AI tutor.",
        title="How it works",
    )
    if st.button("Clear conversation", icon=":material/delete_sweep:"):
        st.session_state.messages = []
        st.rerun()

try:
    classifier = load_classifier()
except (FileNotFoundError, ModuleNotFoundError, ImportError, ValueError) as error:
    st.error(
        "The classifier could not be loaded. Install the versions in "
        "requirements.txt and confirm the model file exists at "
        "dataset/intent_classifier.joblib."
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
            "Can you check 2 + 3 * 4 = 20?",
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
            response = rule_based_reply(intent, prompt)
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
