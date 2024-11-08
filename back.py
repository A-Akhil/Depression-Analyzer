# Flask Backend (server.py)
from flask import Flask, request, jsonify
import ollama
from typing import List
from dataclasses import dataclass
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@dataclass
class QuestionResponse:
    question_number: int
    question_text: str
    student_response: str

@app.route('/assess_depression', methods=['POST'])
def assess_depression():
    responses = [QuestionResponse(**resp) for resp in request.get_json()]
    overall_depression = 0
    result = {
        "responses": [],
        "overall_depression_scale": 0,
        "depression_status": ""
    }

    for response in responses:
        system_prompt = f"""You are an AI model specializing in student mental health assessment. 
        Analyze the following response to assess potential signs of depression: '{response.question_text}'
        The student responded: '{response.student_response}'
        
        Rate on a scale of 1-10 where:
        1 = No signs of depression
        10 = Significant signs of depression
        
        Consider:
        - Emotional state
        - Academic performance
        - Social integration
        - Stress levels
        - Coping mechanisms
        
        Provide only the numerical rating."""
        
        ollama_response = ollama.chat(model='llama3.2', messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": response.student_response}
        ])

        logging.info(f"Question: {response.question_text}")
        logging.info(f"Student response: {response.student_response}")
        logging.info(f"Ollama response: {ollama_response}")

        try:
            depression_text = ollama_response['message']['content']
            import re
            numbers = re.findall(r'\d+', depression_text)
            if numbers:
                depression_scale = numbers[0]
            else:
                depression_scale = '5'
        except (KeyError, IndexError, ValueError) as e:
            logging.error(f"Error parsing Ollama response: {e}")
            depression_scale = '5'

        result["responses"].append({
            "question_number": response.question_number,
            "question_text": response.question_text,
            "student_response": response.student_response,
            "depression_scale": float(depression_scale)
        })
        
        overall_depression += float(depression_scale)

    total_questions = len(responses)
    overall_depression_scale = overall_depression / total_questions

    # Adjusted thresholds for depression risk
    if overall_depression_scale > 7:
        depression_status = "High depression risk"
    elif overall_depression_scale > 4:
        depression_status = "Moderate depression risk"
    else:
        depression_status = "Low depression risk"

    result["overall_depression_scale"] = overall_depression_scale
    result["depression_status"] = depression_status

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)