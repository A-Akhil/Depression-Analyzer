from flask import Flask, request, jsonify
import ollama
from typing import List
from dataclasses import dataclass
import logging
import json

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
        # Updated system prompt with JSON schema
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

        If you are unsure or the response is unclear, still provide a depression score in the range of 1 to 10. If the response is not related to depression, assign a neutral score of 5. 

        Your response should be in the following JSON format:
        {{
          "depression_score": <number between 1 and 10>, 
          "notes": "<any notes or explanation you may have>"
        }}

        Please ensure the response contains both a "depression_score" and "notes" key, even if the assessment is uncertain.
        """

        ollama_response = ollama.chat(model='llama3.2', messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": response.student_response}
        ])

        # Display the question and Ollama's response directly in the terminal
        print(f"Question: {response.question_text}")
        print(f"Ollama response: {ollama_response['message']['content']}")

        try:
            depression_data = ollama_response['message']['content']
            # Expecting the response to be a JSON string in the form of:
            # {"depression_score": <score>, "notes": <any explanation>}
            depression_info = json.loads(depression_data)

            depression_score = depression_info.get('depression_score', 5)
            notes = depression_info.get('notes', 'No specific notes')
        except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing Ollama response: {e}")
            depression_score = 5  # Default score if there's an issue
            notes = "Error in assessment"

        result["responses"].append({
            "question_number": response.question_number,
            "question_text": response.question_text,
            "student_response": response.student_response,
            "depression_score": float(depression_score),
            "notes": notes
        })

        overall_depression += float(depression_score)

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
