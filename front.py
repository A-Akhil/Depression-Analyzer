# Streamlit Frontend (app.py)
import streamlit as st
import requests
import json
from typing import List
from pydantic import BaseModel

st.set_page_config(page_title="Student Depression Assessment", layout="wide")

# Categories of questions
emotional_questions = [
    "How often do you feel overwhelmed by academic pressure?",
    "How frequently do you experience difficulty sleeping?",
    "How often do you feel lonely or isolated at school?",
    "How would you rate your ability to concentrate in class?",
    "How often do you feel hopeless about your academic future?"
]

academic_questions = [
    "How satisfied are you with your current academic performance?",
    "How well can you keep up with assignment deadlines?",
    "How often do you participate in class discussions?",
    "How comfortable are you asking teachers for help?",
    "How well can you maintain your study schedule?"
]

social_questions = [
    "How often do you engage in extracurricular activities?",
    "How comfortable are you working in group projects?",
    "How strong is your support system at school?",
    "How often do you interact with classmates outside of class?",
    "How well do you handle academic competition?"
]

# Streamlit app
st.title("🎓 Student Depression Assessment")
st.write("This assessment helps identify potential signs of depression among students.")

# Create tabs for different categories
tab1, tab2, tab3 = st.tabs(["Emotional Health", "Academic Performance", "Social Integration"])

responses = []

with tab1:
    st.header("Emotional Health Assessment")
    for i, question in enumerate(emotional_questions):
        st.write(f"{i+1}. {question}")
        response = st.text_area(f"Your response (Question {i+1}):", key=f"emotional_{i}")
        responses.append({"question_number": i+1, "question_text": question, "student_response": response})

with tab2:
    st.header("Academic Performance Assessment")
    for i, question in enumerate(academic_questions):
        st.write(f"{i+1}. {question}")
        response = st.text_area(f"Your response (Question {i+1}):", key=f"academic_{i}")
        responses.append({"question_number": i+len(emotional_questions), "question_text": question, "student_response": response})

with tab3:
    st.header("Social Integration Assessment")
    for i, question in enumerate(social_questions):
        st.write(f"{i+1}. {question}")
        response = st.text_area(f"Your response (Question {i+1}):", key=f"social_{i}")
        responses.append({"question_number": i+len(emotional_questions)+len(academic_questions), "question_text": question, "student_response": response})

if st.button("Submit Assessment"):
    # Send responses to backend
    backend_url = "http://localhost:5000/assess_depression"
    response = requests.post(backend_url, json=responses)
    
    if response.status_code == 200:
        result = response.json()
        
        # Display results in an organized manner
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
            for resp in result["responses"][:len(emotional_questions)]:
                st.write(f"- Question {resp['question_number']}: {resp['depression_scale']}/10")
                
        with col2:
            st.write("**Academic Performance Indicators**")
            for resp in result["responses"][len(emotional_questions):len(emotional_questions)+len(academic_questions)]:
                st.write(f"- Question {resp['question_number']}: {resp['depression_scale']}/10")
                
        with col3:
            st.write("**Social Integration Indicators**")
            for resp in result["responses"][len(emotional_questions)+len(academic_questions):]:
                st.write(f"- Question {resp['question_number']}: {resp['depression_scale']}/10")
    else:
        st.error("Error: Unable to process your responses. Please try again later.")