from flask import Flask, request, jsonify, send_file
from core_logic import AutoCorrectAI
from fpdf import FPDF
import os
import pdf_generator

app = Flask(__name__)
ai_engine = AutoCorrectAI()


# Helper to generate PDF (s

def create_pdf_report(grading_data, filename="report.pdf"):
    # Ensure reports directory exists next to this file
    base_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Use SmartPDFGenerator which now accepts lists or dicts
    out_path = os.path.join(reports_dir, filename)
    try:
        # pdf_generator.test_with_various_structures will return the filename
        result_path = pdf_generator.test_with_various_structures(grading_data, out_path)
        return result_path
    except Exception:
        # Fallback simple FPDF dump (keeps existing minimal behavior) -- French labels
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="AutoCorrectGPT - Rapport de notation", ln=1, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', size=12)
        # Try to display any top-level score safely
        total_score = None
        if isinstance(grading_data, dict):
            total_score = grading_data.get('total_score')
        elif isinstance(grading_data, list) and len(grading_data) > 0 and isinstance(grading_data[0], dict):
            total_score = grading_data[0].get('student_score_for_question') or grading_data[0].get('student_score')
        pdf.cell(200, 10, txt=f"Score final : {total_score if total_score is not None else 'N/A'}", ln=1)

        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, txt=str(grading_data))

        pdf.output(out_path)
        return out_path


@app.route('/correct', methods=['POST'])
def correct_copy():
    try:
        data = request.json
        exam_text = data.get('exam_text')
        student_text = data.get('student_text')

        if not exam_text or not student_text:
            return jsonify({"error": "Missing exam_text or student_text"}), 400

        # 1. Extract Rubric
        rubric = ai_engine.extract_rubric(exam_text)

        # 2. Grade Copy
        grading_result = ai_engine.grade_student(rubric, student_text)
        print(grading_result)

        # 3. Generate PDF (saved inside reports folder)
        pdf_path = create_pdf_report(grading_result, filename="report.pdf")

        return jsonify({
            "status": "success",
            "rubric_extracted": rubric,
            "grading_result": grading_result,
            "pdf_report_url": pdf_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)