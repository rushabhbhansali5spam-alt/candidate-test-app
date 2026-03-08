import streamlit as st
import time
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Candidate Test", layout="wide")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZSrHA5Sfuqqt0apwM7EI5dWpMGK4OfaqKKzxE9F1KiYhFpfU3rhFLTZ_KYeDOy8oSQA/exec"

# -----------------------------
# HEADER
# -----------------------------

col1, col2 = st.columns([3,7])

with col1:
    st.image("Final Logo.png", width=320)

with col2:
    st.markdown("""
    <h1 style='margin-bottom:0;'>Klick Consulting</h1>
    <h3 style='margin-top:5px;'>Candidate Assessment Test</h3>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# SESSION VARIABLES
# -----------------------------

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "instructions" not in st.session_state:
    st.session_state.instructions = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "answers" not in st.session_state:
    st.session_state.answers = []

if "last_autosave" not in st.session_state:
    st.session_state.last_autosave = time.time()

# -----------------------------
# CANDIDATE INFO PAGE
# -----------------------------

if st.session_state.start_time is None and not st.session_state.instructions:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")

    cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

    if st.button("Continue"):

        if name and email and phone and cv:

            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone
            st.session_state.cv = cv.name

            st.session_state.instructions = True
            st.rerun()

        else:
            st.error("Please complete all fields including CV.")

# -----------------------------
# INSTRUCTIONS PAGE
# -----------------------------

elif st.session_state.instructions and st.session_state.start_time is None:

    st.header("Test Instructions")

    st.markdown("""
### Please read carefully before starting:

• Total Test Time: **15 Minutes**

• Once the test begins **the timer cannot be paused**

• Do **NOT refresh the page**

• Do **NOT switch browser tabs**

• Ensure you are **sitting alone**

• The test will **auto submit when time ends**

• All answers are **auto saved**

---

### Click below when you are ready.

Good luck!
""")

    if st.button("Start Test"):

        st.session_state.start_time = time.time()
        st.rerun()

# -----------------------------
# TEST PAGE
# -----------------------------

else:

    # refresh page every second for timer
    st_autorefresh(interval=1000, key="timer")

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = 900 - elapsed

    if remaining <= 0:
        remaining = 0
        st.session_state.submitted = True

    mins = remaining // 60
    secs = remaining % 60

    st.markdown(f"## ⏱ Time Remaining: {mins}:{secs:02d}")

# -------------------------------
# QUESTIONS
# -------------------------------

    total_questions = len(questions)

for i,q in enumerate(questions):

        if i not in st.session_state.answers:
            st.session_state.answers[i] = ""

        ans = st.text_area(
            f"Q{i+1}. {q}",
            value=st.session_state.answers[i],
            key=f"q{i}"
        )

        st.session_state.answers[i] = ans


answers = list(st.session_state.answers.values())


# -------------------------------
# PROGRESS BAR
# -------------------------------
answered = len([a for a in answers if a.strip()!=""])
st.progress(answered/total_questions)
st.write(f"Answered {answered} of {total_questions} questions")


# -----------------------------
# AUTO SAVE EVERY 15 SEC
# -----------------------------

if time.time() - st.session_state.last_autosave > 15:

    st.session_state.last_autosave = time.time()

    autosave_payload = {
        "name": st.session_state.name,
        "email": st.session_state.email,
        "phone": st.session_state.phone,
        "cv_link": st.session_state.cv,
        "timestamp": str(datetime.now()),
        "answers": st.session_state.answers,
        "autosave": True
    }

    try:
        requests.post(WEBHOOK_URL, json=autosave_payload)
    except:
        pass
    # -----------------------------
    # SUBMIT BUTTON
    # -----------------------------

    if st.button("Submit Test") or st.session_state.submitted:

        payload = {
            "name": st.session_state.name,
            "email": st.session_state.email,
            "phone": st.session_state.phone,
            "cv_link": st.session_state.cv,
            "timestamp": str(datetime.now()),
            "answers": st.session_state.answers
        }

        try:
            requests.post(WEBHOOK_URL, json=payload)
            st.success("Test submitted successfully!")
        except:
            st.error("Submission failed. Please retry.")
