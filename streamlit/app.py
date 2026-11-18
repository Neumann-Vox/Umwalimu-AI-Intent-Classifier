import re
import streamlit as st

st.set_page_config(page_title="Umwalimu AI | New Student Guide", page_icon="🎓", layout="centered")

WELCOME = """Hello! Welcome to **Umwalimu AI – New Student Guide**.

I can guide you through your first day, registration, orientation, school facilities, basic rules, and student support.

I provide general guidance. Your school’s administration remains the official source for exact rooms, dates, fees, opening hours, and policies."""

ANSWERS = {
    "first_day_guidance": """Welcome to your new school!

**A good place to start is the reception or administration/admissions office.**

Here is a simple first-day checklist:
1. Introduce yourself and confirm that your admission/registration is complete.
2. Ask how to receive your student ID.
3. Request your official timetable.
4. Confirm your class, classroom, and department.
5. Ask whether there is an orientation session or a student guide.

If your school has a designated orientation desk, follow that instruction first. I do not have your school's verified office map, so please confirm the exact location with reception.""",
    "registration_help": """For registration, contact your school's **admissions or administration office**.

Ask them to confirm:
1. Which documents you must submit.
2. Whether any forms are still incomplete.
3. The registration deadline.
4. How to confirm your student status.
5. Where and when to collect your student ID.

Requirements, fees, and deadlines differ by institution. Please use the official school instructions rather than relying on an unverified list.""",
    "student_id_help": """To get your student ID, ask the **administration or student affairs office**.

They can confirm the required documents, collection date, and whether a fee applies. Do not share passwords, PINs, or sensitive identity numbers in this chat.""",
    "facility_location": """I can help you identify the right place, but I do not yet have a verified map of your school.

- **Library:** Ask reception or a teacher for the library location and opening hours.
- **Classroom/laboratory:** Check your timetable and ask your department or class representative.
- **Toilets/cafeteria:** Ask reception or a nearby staff member.
- **Student affairs/health office:** Ask administration to direct you.

Tell me the name of the facility and your school, and I can help you prepare the question to ask. I will not guess room numbers or locations.""",
    "school_rules": """Every school has its own official rules. Please request the student handbook or ask administration for the current policy.

Common areas to check include:
1. Attendance and punctuality.
2. Student conduct and respect.
3. Classroom and laboratory safety.
4. Use of phones and school equipment.
5. Academic honesty.
6. Dress code, if your school has one.

These are topics to verify, not a statement of your school's exact rules.""",
    "orientation_info": """Orientation helps new students understand how the school works and where to get support.

Ask administration or student affairs:
1. When the next orientation takes place.
2. Where students should meet.
3. Whether attendance is required.
4. Whether you should bring any documents.
5. Who your student mentor or class representative is.

I do not have a verified orientation date or venue for your institution.""",
    "student_support": """You do not have to manage a school problem alone.

- For academic questions, speak with your teacher, tutor, or department.
- For registration or administrative issues, contact administration.
- For personal concerns, ask student affairs or a trusted school staff member.
- If you are in immediate danger, being threatened, or need urgent medical help, contact a responsible adult or the school's emergency support immediately.

If you feel comfortable, tell me generally what kind of help you need. Do not share private passwords or sensitive personal information.""",
    "general_school_help": """I can help with new-student questions about:
- What to do on your first day
- Registration and student ID
- Orientation
- School facilities
- School rules
- Finding the right student-support office

Try one of the example questions shown on the page.""",
    "out_of_scope": """I am currently a **New Student Guide**, not a general-purpose chatbot.

Please ask about first-day guidance, registration, student ID, orientation, school facilities, school rules, or student support."""
}

RULES = [
    ("student_support", ["bullying", "bullied", "harass", "threat", "unsafe", "abuse", "hurt myself", "emergency", "medical emergency", "someone is hurting", "personal problem", "counsellor", "counselor", "student affairs", "struggling with school work"]),
    ("first_day_guidance", ["where should i go first", "where do i go first", "first day", "new student", "i am new", "im new", "just joined", "new here", "start at school"]),
    ("registration_help", ["registration", "register", "admission", "admissions", "enrol", "enrollment", "enrolment", "documents", "fees", "tuition"]),
    ("student_id_help", ["student id", "school id", "identity card", "id card", "student card"]),
    ("facility_location", ["where is", "where can i find", "location of", "library", "laboratory", "lab", "classroom", "toilet", "washroom", "cafeteria", "canteen", "computer room", "office"]),
    ("school_rules", ["school rules", "rules", "regulations", "dress code", "uniform", "attendance", "punctuality", "phone policy", "discipline"]),
    ("orientation_info", ["orientation", "induction", "welcome session", "orientation date", "orientation time"]),
    ("general_school_help", ["what can you do", "how can you help", "what can i ask", "help me"]),
]

def normalize(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()

def detect_intent(message):
    text = normalize(message)
    for intent, phrases in RULES:
        if any(phrase in text for phrase in phrases):
            return intent
    if text in {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "muraho", "mwaramutse"}:
        return "greeting"
    if any(word in text for word in ["thank you", "thanks", "murakoze"]):
        return "gratitude"
    if any(word in text for word in ["bye", "goodbye", "see you"]):
        return "farewell"
    return "out_of_scope"

def answer(message):
    intent = detect_intent(message)
    if intent == "greeting":
        return ("Hello! Welcome to Umwalimu AI. Are you a new student?\n\n"
                "I can help you with your first day, registration, student ID, orientation, "
                "school facilities, school rules, and student support.\n\n"
                "**What would you like help with first?**")
    if intent == "gratitude":
        return "You’re welcome! I’m happy to help. What would you like to know about your school?"
    if intent == "farewell":
        return "Goodbye! I wish you a successful and enjoyable experience at your new school."
    return ANSWERS[intent]

st.title("🎓 Umwalimu AI")
st.subheader("New Student Guide")
st.caption("Simple, reliable guidance to help you get started at school.")

with st.expander("Example questions — select one to try", expanded=True):
    examples = [
        "Hello",
        "I am new. Where should I go first?",
        "How do I complete my registration?",
        "How can I get my student ID?",
        "Where is the library?",
        "What are the school rules?",
        "When is student orientation?",
        "I need help with a personal problem.",
    ]
    for question in examples:
        if st.button(question, key="example_" + str(examples.index(question)), use_container_width=True):
            st.session_state.pending_question = question

with st.sidebar:
    st.markdown("### About this guide")
    st.write("This version answers common new-student questions using fixed, reviewed response templates.")
    st.info("Exact school-specific locations, dates, fees, and policies must be confirmed by your institution.")
    if st.button("Start a new chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = ""
        st.rerun()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("pending_question", "")

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

prompt = st.chat_input("Ask a question about starting at school…")
if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = answer(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

if not st.session_state.messages:
    st.markdown("### Start here")
    st.write("Type **Hello** to begin. I will welcome you and show you what you can ask next.")
