import os
import google.generativeai as genai
import json
import typing_extensions as typing
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API Key not found! Make sure you created a .env file.")

genai.configure(api_key=api_key)


class AutoCorrectAI:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_rubric(self, exam_text):
        """
        Step 1: Extract the grading criteria (Barème) from the exam paper.
        """
        prompt = f"""
        Act as an expert pedagogical engineer. Analyze the following Exam Paper.
        Extract the grading rubric into a structured JSON format.
        For each question or section, identify:
        - The question ID/Number.
        - The topic.
        - The maximum points assigned.
        - The key elements expected in the answer (keywords, concepts).

        EXAM PAPER:
        {exam_text}
        """

        # Enforce JSON output schema
        result = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(result.text)

    def grade_student(self, rubric_json, student_copy):
        """
        Step 2: Grade the student copy based ONLY on the extracted rubric.
        """
        prompt = f"""
        Act as a strict but fair academic grader. 

        INPUT DATA:
        1. RUBRIC (JSON): {json.dumps(rubric_json)}
        2. STUDENT COPY: {student_copy}

        INSTRUCTIONS:
        - Go through the rubric item by item.
        - Compare the student's answer to the "expected elements".
        - Assign a score for each item (do not exceed max points).
        - Provide a justification for the score (mention missing keywords or logic errors).
        - Calculate the final total score.

        Output valid JSON.
        """

        result = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(result.text)

if __name__ == "__main__":
    ai_engine = AutoCorrectAI()
    print("all good")