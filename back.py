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
    data = request.get_json()
    user_type = data.get('user_type', 'Student')
    responses = [
        QuestionResponse(
            resp.get('question_number', 0),
            resp.get('question_text', ''),
            resp.get('student_response', '')
        )
        for resp in data.get('responses', [])
    ]

    overall_depression = 0
    result = {
        "responses": [],
        "overall_depression_scale": 0,
        "depression_status": ""
    }

    for response in responses:
        system_prompt = f"""You are an AI model specializing in student mental health assessment. Your task is to assess potential signs of depression based on the student's response to a given question.

        Here’s the question for your assessment:
        - Question: '{response.question_text}'
        - Student's Response: '{response.student_response}'

        Your Task:
        - Rate the response on a scale of 1 to 10 for signs of depression:
        - 1-2: No signs of depression.
        - 3-4: Mild signs of depression.
        - 5-6: Moderate signs of depression.
        - 7-8: Noticeable signs of depression.
        - 9-10: Significant signs of depression.
        """

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
            depression_scale = numbers[0] if numbers else '5'
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
    overall_depression_scale = overall_depression / total_questions if total_questions > 0 else 0

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
