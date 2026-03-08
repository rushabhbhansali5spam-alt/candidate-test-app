import streamlit as st
import time
import requests
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="Candidate Test", layout="wide")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzZSrHA5Sfuqqt0apwM7EI5dWpMGK4OfaqKKzxE9F1KiYhFpfU3rhFLTZ_KYeDOy8oSQA/exec"

TEST_DURATION = 900

# -------------------------------
# HEADER WITH LOGO
# -------------------------------

col1, col2 = st.columns([1,5])

with col1:
    st.image("Final Logo.png", width=120)

with col2:
    st.markdown("## Klick Consulting")
    st.markdown("### Candidate Assessment Test")

st.divider()


# -------------------------------
# SESSION STATE
# -------------------------------

if "step" not in st.session_state:
    st.session_state.step = 1

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
    r = requests.get(WEBHOOK_URL)
    return [q.replace("\n"," ") for q in r.json()]

questions = load_questions()


# -------------------------------
# PDF GENERATOR
# -------------------------------

def generate_pdf(name,email,answers):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"Candidate Assessment Test",ln=True)

    pdf.set_font("Arial","",12)
    pdf.cell(0,10,f"Name: {name}",ln=True)
    pdf.cell(0,10,f"Email: {email}",ln=True)
    pdf.cell(0,10,f"Date: {datetime.now()}",ln=True)

    pdf.ln(10)

    for i,(q,a) in enumerate(zip(questions,answers)):
        pdf.multi_cell(0,8,f"Q{i+1}. {q}")
        pdf.multi_cell(0,8,f"Answer: {a}")
        pdf.ln(3)

    filename = f"{name}_answers.pdf"
    pdf.output(filename)

    return filename


# -------------------------------
# STEP 1: CANDIDATE INFO
# -------------------------------

if st.session_state.step == 1:

    st.header("Candidate Information")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Mobile Number")

    if st.button("Continue"):

        if name and email and phone:

            st.session_state.name = name
            st.session_state.email = email
            st.session_state.phone = phone

            st.session_state.step = 2
            st.rerun()

        else:
            st.error("Please fill all fields.")


# -------------------------------
# STEP 2: INSTRUCTIONS
# -------------------------------

elif st.session_state.step == 2:

    st.header("Test Instructions")

    st.markdown(f"""
### Please read carefully before starting:

⏱ **Duration:** 15 Minutes  
📄 **Total Questions:** {len(questions)}

---

### Rules

• Do not refresh the page  
• Do not switch browser tabs  
• Do not open other websites  
• Sit alone and complete the test honestly  
• Once the timer ends, the test will **auto submit**

---

### Good Luck 👍
""")

    if st.button("Start Test Now"):

        st.session_state.start_time = time.time()
        st.session_state.step = 3
        st.rerun()


# -------------------------------
# STEP 3: TEST
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


    # -------------------------------
    # SUBMIT TEST
    # -------------------------------

    if (st.button("Submit Test") or st.session_state.submitted) and not st.session_state.get("final_submit",False):

        st.session_state.final_submit = True

        payload = {
            "name": st.session_state.name,
            "email": st.session_state.email,
            "phone": st.session_state.phone,
            "timestamp": str(datetime.now()),
            "answers": answers
        }

        try:

            requests.post(WEBHOOK_URL,json=payload)

            pdf_file = generate_pdf(
                st.session_state.name,
                st.session_state.email,
                answers
            )

            with open(pdf_file,"rb") as f:
                st.download_button(
                    "Download Your Answer Sheet",
                    f,
                    file_name=pdf_file
                )

            st.success("Test submitted successfully!")

        except:
            st.error("Submission failed.")


    # TIMER REFRESH
    time.sleep(1)
    st.rerun()
