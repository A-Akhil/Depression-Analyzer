import csv
import ollama
import random
from datetime import datetime
import time

# Depression assessment questions
questions = [
    "How have you been sleeping lately?",
    "How would you describe your energy levels throughout the day?",
    "How has your appetite been recently?",
    "How well can you concentrate on tasks?",
    "Do you feel hopeless about the future?",
    "Have you lost interest in activities you usually enjoy?",
    "How often do you feel tired or have little energy?",
    "How do you feel about yourself and your self-worth?",
    "Do you feel lonely or isolated?",
    "Are you having trouble handling daily responsibilities?"
]

def get_ollama_response(question):
    system_prompt = """You are simulating a student responding to mental health assessment questions. 
                    Provide a realistic response in 1-2 sentences, as if you were a student potentially experiencing depression. 
                    Keep your answers brief and direct based on the question below:
                    """
    print(f"🧠 Sending question to Ollama: '{question}'")
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ])
        
        # Extract the content from the response
        print(f"💬 Response received: {response['message']['content']}")
        return response['message']['content']
    except Exception as e:
        print(f"❌ Error processing response: {str(e)}")
        return "No response"

def generate_dataset(num_samples=100, output_file='depression_dataset.csv'):
    print(f"📂 Preparing to generate dataset with {num_samples} samples...")
    
    # Define CSV headers
    headers = [
        's no',
        'age',
        'gender'
    ] + questions + ["scale of 1 to 10"]

    print(f"📝 Opening file '{output_file}' for writing...")
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        print("✅ CSV file initialized with headers.")

        for i in range(num_samples):
            print(f"\n➡️ Processing sample {i+1}/{num_samples}")

            # Generate demographic data
            age = random.randint(17, 21)
            gender = random.choice(['M', 'F'])
            
            print(f"👤 Generated demographic data - Age: {age}, Gender: {gender}")
            
            # Write initial data
            row = {
                's no': i + 1,
                'age': age,
                'gender': gender
            }
            
            # For each question, get a response and write it directly to the CSV row
            for index, question in enumerate(questions):
                print(f"📝 Question {index+1}/{len(questions)}: '{question}'")
                response = get_ollama_response(question)
                row[question] = response
            
            # Generate a random depression level rating between 1 and 10
            depression_scale = random.randint(1, 10)
            row["scale of 1 to 10"] = depression_scale
            print(f"📊 Generated depression scale: {depression_scale}")

            # Write the row to the CSV file
            try:
                writer.writerow(row)
                print(f"✅ Sample {i+1} successfully written to CSV")
            except Exception as e:
                print(f"❌ Error writing sample {i+1} to CSV: {str(e)}")
            
            # Add a small delay to avoid overwhelming the API
            # time.sleep(1)

    print(f"\n✨ Dataset generation complete! File saved as: {output_file}")

if __name__ == "__main__":
    print("🔄 Initializing Depression Dataset Generator...")
    start_time = datetime.now()
    generate_dataset(num_samples=300)
    end_time = datetime.now()
    print(f"⏰ Time taken for dataset generation: {end_time - start_time}")
    print("🚀 Process completed!")
