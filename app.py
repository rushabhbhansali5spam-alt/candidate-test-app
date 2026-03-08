from streamlit_autorefresh import st_autorefresh
import streamlit as st
import time
import requests
from datetime import datetime

st.set_page_config(page_title="Candidate Test", layout="wide")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZSrHA5Sfuqqt0apwM7EI5dWpMGK4OfaqKKzxE9F1KiYhFpfU3rhFLTZ_KYeDOy8oSQA/exec"

TEST_DURATION = 900   # 15 minutes

st.title("Candidate Assessment Test")
st_autorefresh(interval=1000, key="timer")

# -------------------------------
# SESSION STATE
# -------------------------------

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False


# -------------------------------
# LOAD QUESTIONS
# -------------------------------

@st.cache_data
def load_questions():
    response = requests.get(WEBHOOK_URL)
    return [q.replace("\n"," ") for q in response.json()]


questions = load_questions()


# -------------------------------
# CANDIDATE INFO PAGE
# -------------------------------

if st.session_state.start_time is None:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")
    cv = st.file_uploader("Upload CV")

    if st.button("Start Test"):

        if name and email and phone:

            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone
            st.session_state.start_time = time.time()

            st.rerun()

        else:
            st.error("Please fill all fields before starting.")


# -------------------------------
# TEST PAGE
# -------------------------------

else:

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = TEST_DURATION - elapsed

    if remaining <= 0:
        remaining = 0
        st.session_state.submitted = True

    mins = remaining // 60
    secs = remaining % 60

    st.markdown(f"## ⏱ Time Remaining: {mins:02d}:{secs:02d}")


    # -------------------------------
    # QUESTIONS
    # -------------------------------

    total_questions = len(questions)

    for i, q in enumerate(questions):

        if i not in st.session_state.answers:
            st.session_state.answers[i] = ""

        answer = st.text_area(
            f"Q{i+1}. {q}",
            value=st.session_state.answers[i],
            key=f"q{i}"
        )

        st.session_state.answers[i] = answer


    answers = list(st.session_state.answers.values())


    # -------------------------------
    # PROGRESS
    # -------------------------------

    answered = len([a for a in answers if a.strip() != ""])

    st.progress(answered / total_questions)
    st.write(f"Answered {answered} of {total_questions} questions")


    # -------------------------------
    # SUBMIT
    # -------------------------------

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
            st.error("Submission failed. Please retry.")
