import streamlit as st
import requests
import json
from typing import List

st.set_page_config(page_title="Depression Assessment", layout="wide")

# Sidebar user type selection
st.sidebar.header("User Type")
user_type = st.sidebar.radio("Select User Type:", ["Student", "Faculty"])

# Sidebar progress tracking
def calculate_progress(responses, total_questions):
    answered = sum(1 for resp in responses if resp["student_response"].strip() != "")
    return (answered / total_questions) * 100

# Define questions for Student
student_questions = {
    "emotional": [
        "How often do you feel overwhelmed by academic pressure?",
        "How frequently do you experience difficulty sleeping?",
        "How often do you feel lonely or isolated at collage?",
        "How would you rate your ability to concentrate in class?",
        "How often do you feel hopeless about your academic future?"
    ],
    "academic": [
        "How satisfied are you with your current academic performance?",
        "How well can you keep up with assignment deadlines?",
        "How often do you participate in class discussions?",
        "How comfortable are you asking teachers for help?",
        "How well can you maintain your study schedule?"
    ],
    "social": [
        "How often do you engage in extracurricular activities?",
        "How comfortable are you working in group projects?",
        "How strong is your support system at collage?",
        "How often do you interact with classmates outside of class?",
        "How well do you handle academic competition?"
    ]
}

# Define questions for Faculty
faculty_questions = {
    "emotional": [
        "How often do you feel overwhelmed by your workload?",
        "How frequently do you experience burnout symptoms?",
        "How often do you feel unsupported by your peers or administration?",
        "How would you rate your job satisfaction?",
        "How often do you feel stressed about your teaching performance?"
    ],
    "academic": [
        "How satisfied are you with your students' academic progress?",
        "How well do you manage your class schedules?",
        "How often do you engage in professional development activities?",
        "How comfortable are you with current teaching methods?",
        "How well do you balance teaching and research responsibilities?"
    ],
    "social": [
        "How often do you participate in faculty meetings?",
        "How comfortable are you collaborating with other faculty members?",
        "How strong is your support system at work?",
        "How often do you engage in social activities with colleagues?",
        "How well do you handle administrative pressures?"
    ]
}

# Select questions based on user type
questions = student_questions if user_type == "Student" else faculty_questions

# Initialize responses list
responses = []

# Streamlit app
st.title("🧠 Depression Assessment")
st.write(f"This assessment helps identify potential signs of depression among {user_type.lower()}s.")

# Sidebar progress
total_questions = sum(len(q_list) for q_list in questions.values())
progress = calculate_progress(responses, total_questions)
st.sidebar.header("📝 Assessment Progress")
progress_bar = st.sidebar.progress(progress / 100)

# Create tabs for different categories
tab1, tab2, tab3 = st.tabs(["Emotional Health", "Academic Performance", "Social Integration"])

for tab, category in zip([tab1, tab2, tab3], ["emotional", "academic", "social"]):
    with tab:
        st.header(f"{category.capitalize()} Assessment")
        for i, question in enumerate(questions[category]):
            st.write(f"**{i + 1}. {question}**")
            response = st.text_area(f"Your response (Question {i + 1}):", key=f"{category}_{i}")
            responses.append({
                "question_number": i + 1,
                "question_text": question,
                "student_response": response
            })

# Update progress bar after all responses
progress = calculate_progress(responses, total_questions)
progress_bar.progress(progress / 100)

# Show submit button only if all questions are answered
all_answered = all(resp["student_response"].strip() != "" for resp in responses)
if all_answered:
    if st.button("Submit Assessment"):
        with st.spinner('Analyzing your responses, please wait...'):
            backend_url = "http://localhost:5000/assess_depression"
            payload = {
                "user_type": user_type,
                "responses": responses
            }
            response = requests.post(backend_url, json=payload)

            if response.status_code == 200:
                result = response.json()
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Overall Depression Risk Score", f"{result['overall_depression_scale']:.2f}/10")
                    
                with col2:
                    status_color = {
                        "High depression risk": "🔴",
                        "Moderate depression risk": "🟡",
                        "Low depression risk": "🟢"
                    }
                    st.write(f"Status: {status_color.get(result['depression_status'], '')} {result['depression_status']}")
                
                # Show detailed breakdown
                st.subheader("Detailed Assessment")
                
                # Create three columns for different categories
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Emotional Health Indicators**")
                    for resp in result["responses"][:len(questions['emotional'])]:
                        st.write(f"- Question {resp['question_number']}: {resp['depression_score']}/10")
                        
                with col2:
                    st.write("**Academic Performance Indicators**")
                    for resp in result["responses"][len(questions['emotional']):len(questions['emotional'])+len(questions['academic'])]:
                        st.write(f"- Question {resp['question_number']}: {resp['depression_score']}/10")
                        
                with col3:
                    st.write("**Social Integration Indicators**")
                    for resp in result["responses"][len(questions['emotional'])+len(questions['academic']):]:
                        st.write(f"- Question {resp['question_number']}: {resp['depression_score']}/10")

            else:
                st.error("Error: Unable to process your responses. Please try again later.")
else:
    st.warning("Please answer all questions to submit the assessment.")
