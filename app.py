import streamlit as st
import time
import requests
from datetime import datetime

st.set_page_config(page_title="Candidate Test", layout="wide")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZSrHA5Sfuqqt0apwM7EI5dWpMGK4OfaqKKzxE9F1KiYhFpfU3rhFLTZ_KYeDOy8oSQA/exec"

ADMIN_PASSWORD = "admin123"

st.title("Candidate Assessment Test")

# -------------------------------
# Session State Setup
# -------------------------------

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False


# -------------------------------
# ADMIN PANEL
# -------------------------------

with st.sidebar:

    st.header("Admin")

    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):

        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged = True
        else:
            st.error("Wrong password")

    if st.session_state.admin_logged:

        st.success("Admin Logged In")

        try:
            response = requests.get(WEBHOOK_URL + "?responses=1")
            data = response.json()

            st.write("### Candidate Responses")
            st.dataframe(data)

        except:
            st.warning("Responses API not configured")

# -------------------------------
# Candidate Info Page
# -------------------------------

if st.session_state.start_time is None:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")
    cv = st.file_uploader("Upload CV")

    if st.button("Start Test"):

        if name and email and phone:

            # Check duplicate attempt
            try:
                existing = requests.get(WEBHOOK_URL + "?check_email=" + email).json()

                if existing:
                    st.error("You have already attempted this test.")
                    st.stop()

            except:
                pass

            st.session_state.start_time = time.time()
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone

            st.rerun()

        else:
            st.error("Please fill all fields before starting.")

# -------------------------------
# Test Page
# -------------------------------

else:

    TEST_DURATION = 900

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = TEST_DURATION - elapsed

    if remaining <= 0:
        st.warning("Time is up. Auto submitting.")
        st.session_state.submitted = True
        remaining = 0

    mins = remaining // 60
    secs = remaining % 60

    timer = st.empty()
    timer.markdown(f"## ⏱ Time Remaining: {mins:02d}:{secs:02d}")

    # Fetch questions
    response = requests.get(WEBHOOK_URL)
    questions = [q.replace("\n"," ") for q in response.json()]

    total_questions = len(questions)

    for i, q in enumerate(questions):

        if i not in st.session_state.answers:
            st.session_state.answers[i] = ""

        ans = st.text_area(
            f"Q{i+1}. {q}",
            value=st.session_state.answers[i],
            key=f"q{i}"
        )

        st.session_state.answers[i] = ans

    answers = list(st.session_state.answers.values())

    # Progress Indicator
    answered = len([a for a in answers if a.strip() != ""])

    st.progress(answered / total_questions)

    st.write(f"Answered {answered} of {total_questions} questions")

    # Submit logic
    if (st.button("Submit Test") or st.session_state.submitted) and not st.session_state.get("final_submit", False):

        st.session_state.final_submit = True

        payload = {
            "name": st.session_state.name,
            "email": st.session_state.email,
            "phone": st.session_state.phone,
            "cv_link": "",
            "timestamp": str(datetime.now()),
            "answers": answers
        }

        try:
            requests.post(WEBHOOK_URL, json=payload)
            st.success("Test submitted successfully!")
        except:
            st.error("Submission failed.")

    # refresh timer
    time.sleep(1)
    st.rerun()
