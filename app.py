import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime

st.set_page_config(page_title="Candidate Test", layout="wide")

# Your webhook URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby-XRF2JQdcaZGVimtKwVVupvovFZ7G0uMttV4uA4f8tgC6fZe_0lcXkAZiwy2oNCcT4A/exec"

st.title("Candidate Assessment Test")

# Session variables
if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False


# Candidate info page
if st.session_state.start_time is None:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")
    cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

    if st.button("Start Test"):

        if name and email and phone:
            st.session_state.start_time = time.time()
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone
            st.rerun()

        else:
            st.error("Please fill all details before starting the test")


# Test page
else:

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = 900 - elapsed

    if remaining <= 0:
        st.warning("Time is up. Auto submitting.")
        st.session_state.submitted = True

    mins = remaining // 60
    secs = remaining % 60

    st.markdown(f"## ⏱ Time Remaining: {mins}:{secs:02d}")

 response = requests.get(WEBHOOK_URL)
questions = response.json()

answers = []

for i, q in enumerate(questions):
    ans = st.text_area(q, key=i)
    answers.append(ans)

    if st.button("Submit Test") or st.session_state.submitted:

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
