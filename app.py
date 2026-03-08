import streamlit as st
import time
import requests
from datetime import datetime

st.set_page_config(page_title="Candidate Test", layout="wide")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZSrHA5Sfuqqt0apwM7EI5dWpMGK4OfaqKKzxE9F1KiYhFpfU3rhFLTZ_KYeDOy8oSQA/exec"

# -----------------------
# HEADER
# -----------------------

col1, col2 = st.columns([3,7])

with col1:
    st.image("Final Logo.png", width=320)

with col2:
    st.markdown("""
    <h1 style='margin-bottom:0'>Klick Consulting</h1>
    <h3 style='margin-top:5px'>Candidate Assessment Test</h3>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------
# SESSION STATE
# -----------------------

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "answers" not in st.session_state:
    st.session_state.answers = []

if "last_autosave" not in st.session_state:
    st.session_state.last_autosave = time.time()

# -----------------------
# CANDIDATE INFO PAGE
# -----------------------

if st.session_state.start_time is None:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")

    cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

    if st.button("Continue"):

        if name and email and phone and cv:

            st.session_state.start_time = time.time()
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone
            st.session_state.cv = cv.name

            st.rerun()

        else:
            st.error("Please complete all fields including CV.")

# -----------------------
# TEST PAGE
# -----------------------

else:

    # TIMER PLACEHOLDER
    timer_placeholder = st.empty()

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = 900 - elapsed

    if remaining <= 0:
        remaining = 0
        st.session_state.submitted = True

    mins = remaining // 60
    secs = remaining % 60

    timer_placeholder.markdown(f"## ⏱ Time Remaining: {mins}:{secs:02d}")

    # -----------------------
    # LOAD QUESTIONS
    # -----------------------

    response = requests.get(WEBHOOK_URL)
    questions = response.json()

    if len(st.session_state.answers) == 0:
        st.session_state.answers = [""] * len(questions)

    answers = []

    for i, q in enumerate(questions):

        ans = st.text_area(
            f"Q{i+1}. {q}",
            value=st.session_state.answers[i],
            key=f"q{i}"
        )

        answers.append(ans)

    st.session_state.answers = answers

    # -----------------------
    # AUTO SAVE
    # -----------------------

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

    # -----------------------
    # SUBMIT BUTTON
    # -----------------------

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

    # -----------------------
    # LIVE TIMER LOOP
    # -----------------------

    time.sleep(1)
    st.rerun()
