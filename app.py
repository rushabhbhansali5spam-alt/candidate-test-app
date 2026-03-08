import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import time
from datetime import datetime

# Google setup
scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Candidate_Test_DB")
questions_sheet = sheet.worksheet("Questions")
responses_sheet = sheet.worksheet("Responses")

drive_service = build("drive", "v3", credentials=creds)

FOLDER_ID = "14DRwl04uRrx98-ic9bb9ck-NTuM5IgZ-"

st.set_page_config(page_title="Candidate Test")

menu = st.sidebar.selectbox("Menu",["Candidate Test","Admin"])

# Load questions
questions = questions_sheet.col_values(1)[1:]

if menu == "Candidate Test":

    st.title("Candidate Assessment")

    if "start_time" not in st.session_state:
        st.session_state.start_time = None

    if st.session_state.start_time is None:

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        cv = st.file_uploader("Upload CV")

        existing_emails = responses_sheet.col_values(2)

        if st.button("Start Test"):

            if email in existing_emails:
                st.error("You have already taken this test.")
            elif name and email:
                st.session_state.start_time = time.time()
                st.session_state.name = name
                st.session_state.email = email
                st.session_state.phone = phone
                st.session_state.cv = cv
                st.rerun()

    else:

        elapsed = int(time.time() - st.session_state.start_time)
        remaining = 900 - elapsed

        mins = remaining // 60
        secs = remaining % 60

        st.markdown(f"### ⏱ Time Remaining: {mins}:{secs:02d}")

        answers = []

        for i,q in enumerate(questions):
            ans = st.text_area(q,key=i)
            answers.append(ans)

        if st.button("Submit") or remaining <= 0:

            cv_link = ""

            if st.session_state.cv:

                file = st.session_state.cv
                file_bytes = io.BytesIO(file.read())

                media = MediaIoBaseUpload(file_bytes,mimetype=file.type)

                file_metadata = {
                    "name": file.name,
                    "parents":[FOLDER_ID]
                }

                uploaded = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()

                cv_link = f"https://drive.google.com/file/d/{uploaded['id']}"

            responses_sheet.append_row([
                st.session_state.name,
                st.session_state.email,
                st.session_state.phone,
                cv_link,
                str(datetime.now()),
                *answers
            ])

            st.success("Test submitted successfully!")

if menu == "Admin":

    password = st.text_input("Enter admin password",type="password")

    if password == "Klick@123":

        st.title("Admin Dashboard")

        data = responses_sheet.get_all_records()
        df = pd.DataFrame(data)

        st.dataframe(df)

        st.download_button(
            "Download Excel",
            df.to_excel("responses.xlsx",index=False),
            "responses.xlsx"
        )