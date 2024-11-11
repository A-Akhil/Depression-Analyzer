from flask import Flask, request, jsonify
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import os
from dataclasses import dataclass
import logging
from typing import List

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
MAX_LENGTH = 128
MODEL_PATH = "models/depression_roberta"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@dataclass
class StudentResponse:
    question_number: int
    question_text: str
    response_text: str

class DepressionDetector:
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained(MODEL_PATH)
        self.model = RobertaForSequenceClassification.from_pretrained(
            MODEL_PATH,
            num_labels=5  # 5 levels of depression severity
        ).to(DEVICE)
        self.model.eval()

    def preprocess_text(self, text: str) -> torch.Tensor:
        encoded = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=MAX_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoded['input_ids'].to(DEVICE),
            'attention_mask': encoded['attention_mask'].to(DEVICE)
        }

    def predict_depression_level(self, text: str) -> dict:
        inputs = self.preprocess_text(text)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=1)
            depression_score = torch.argmax(predictions).item()
            confidence = predictions[0][depression_score].item()

        return {
            'depression_score': depression_score + 1,  # 1-5 scale
            'confidence': round(confidence * 100, 2)
        }

# Initialize the detector
detector = DepressionDetector()

@app.route('/assess_depression', methods=['POST'])
def assess_depression():
    try:
        data = request.get_json()
        responses = [
            StudentResponse(
                resp.get('question_number', 0),
                resp.get('question_text', ''),
                resp.get('response_text', '')
            )
            for resp in data.get('responses', [])
        ]

        results = {
            "responses": [],
            "overall_depression_score": 0,
            "risk_level": ""
        }

        total_score = 0
        for response in responses:
            # Combine question and answer for context
            analysis_text = f"Question: {response.question_text} Answer: {response.response_text}"
            
            # Get prediction
            prediction = detector.predict_depression_level(analysis_text)
            
            results["responses"].append({
                "question_number": response.question_number,
                "question_text": response.question_text,
                "response_text": response.response_text,
                "depression_score": prediction['depression_score'],
                "confidence": prediction['confidence']
            })
            
            total_score += prediction['depression_score']

        # Calculate overall score
        avg_score = total_score / len(responses) if responses else 0
        results["overall_depression_score"] = round(avg_score, 2)

        # Determine risk level
        if avg_score >= 4:
            results["risk_level"] = "High Risk"
        elif avg_score >= 3:
            results["risk_level"] = "Moderate Risk"
        elif avg_score >= 2:
            results["risk_level"] = "Low Risk"
        else:
            results["risk_level"] = "Minimal Risk"

        return jsonify(results)

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)