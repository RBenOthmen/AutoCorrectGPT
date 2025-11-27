from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
import re
import os


class SmartPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.darkblue
        )

        self.subheading_style = ParagraphStyle(
            'Subheading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.darkblue
        )

        self.normal_style = self.styles['Normal']
        self.bold_style = ParagraphStyle(
            'BoldStyle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold'
        )
    
    def _escape_html(self, text):
        """Escape special characters for ReportLab Paragraph"""
        if not isinstance(text, str):
            text = str(text)
        # Escape special XML/HTML characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        # Keep single quotes and other characters as-is for ReportLab
        return text

    def ai_detect_keys(self, data):
        """
        Use pattern matching and AI-like logic to detect key types
        """
        key_categories = {
            'identification': {
                'patterns': ['id', 'question', 'name', 'identifier', 'number'],
                'keys': []
            },
            'topic': {
                'patterns': ['topic', 'subject', 'theme', 'title', 'content'],
                'keys': []
            },
            'score_info': {
                'patterns': ['score', 'points', 'mark', 'grade', 'total', 'maximum'],
                'keys': []
            },
            'answer': {
                'patterns': ['answer', 'response', 'solution', 'student'],
                'keys': []
            },
            'breakdown': {
                'patterns': ['breakdown', 'rubric', 'criteria', 'grading', 'elements'],
                'keys': []
            },
            'feedback': {
                'patterns': ['feedback', 'comment', 'review', 'evaluation'],
                'keys': []
            }
        }

        # Analyze first item to detect keys
        if data and len(data) > 0:
            first_item = data[0]

            for key in first_item.keys():
                key_lower = key.lower()

                # Check each category
                for category, info in key_categories.items():
                    for pattern in info['patterns']:
                        if pattern in key_lower:
                            key_categories[category]['keys'].append(key)
                            break

        return key_categories

    def extract_question_info(self, item, key_categories):
        """Extract question information using detected keys"""
        info = {}

        # Extract identification
        for key in key_categories['identification']['keys']:
            if key in item:
                info['question_id'] = str(item[key])
                break
        else:
            info['question_id'] = "Unknown Question"

        # Extract topic
        for key in key_categories['topic']['keys']:
            if key in item:
                info['topic'] = str(item[key])
                break
        else:
            info['topic'] = "No Topic"

        # Extract scores
        score_keys = key_categories['score_info']['keys']
        info['max_points'] = self.find_numeric_value(item, score_keys, ['max', 'maximum', 'total'])
        info['student_score'] = self.find_numeric_value(item, score_keys, ['student', 'actual', 'achieved', 'score'])

        # Extract answer
        for key in key_categories['answer']['keys']:
            if key in item:
                info['student_answer'] = str(item[key])
                break
        else:
            info['student_answer'] = "No answer provided"

        # Extract breakdown
        for key in key_categories['breakdown']['keys']:
            if key in item and isinstance(item[key], list):
                info['grading_breakdown'] = item[key]
                break
        else:
            info['grading_breakdown'] = []

        # Extract feedback
        for key in key_categories['feedback']['keys']:
            if key in item:
                info['overall_feedback'] = str(item[key])
                break
        else:
            info['overall_feedback'] = "No feedback provided"

        return info

    def find_numeric_value(self, item, score_keys, patterns):
        """Find numeric values based on key patterns"""
        for pattern in patterns:
            for key in score_keys:
                if pattern in key.lower() and key in item:
                    value = item[key]
                    if isinstance(value, (int, float)):
                        return value
                    elif isinstance(value, str):
                        # Try to extract number from string
                        numbers = re.findall(r'\d+\.?\d*', value)
                        if numbers:
                            return float(numbers[0])
        return 0

    def analyze_breakdown_structure(self, breakdown_item):
        """Analyze the structure of grading breakdown items"""
        if not breakdown_item:
            return {}

        structure = {
            'element': [],
            'max_points': [],
            'score': [],
            'justification': []
        }

        first_element = breakdown_item[0] if breakdown_item else {}

        for key in first_element.keys():
            key_lower = key.lower()

            if any(pattern in key_lower for pattern in ['element', 'criterion', 'rubric', 'part']):
                structure['element'].append(key)
            elif any(pattern in key_lower for pattern in ['max', 'maximum', 'total']):
                structure['max_points'].append(key)
            elif any(pattern in key_lower for pattern in ['score', 'student', 'points', 'earned']):
                structure['score'].append(key)
            elif any(pattern in key_lower for pattern in ['justification', 'reason', 'comment', 'feedback']):
                structure['justification'].append(key)

        return structure

    def generate_pdf(self, data, filename="grading_report.pdf"):
        """Main function to generate PDF from variable JSON data"""
        if not data:
            raise ValueError("No data provided")

        # Normalize input: accept dict (maybe containing 'corrections') or list of question dicts
        if isinstance(data, dict):
            # prefer explicit 'corrections' key if present
            if 'corrections' in data and isinstance(data['corrections'], list):
                data = data['corrections']
            else:
                # treat single question dict as one-item list
                data = [data]
        elif isinstance(data, list):
            # already list - OK
            pass
        else:
            raise TypeError("Unsupported data type for PDF generation. Expect dict or list of dicts.")

        # Ensure output directory exists
        out_dir = os.path.dirname(filename) or "."
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Analyze the data structure
        key_categories = self.ai_detect_keys(data)

        # Create document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # Title (French)
        story.append(Paragraph("Rapport d'évaluation généré par l'IA", self.title_style))
        story.append(Spacer(1, 0.3 * inch))

        for item in data:
            # Extract information using AI detection
            question_info = self.extract_question_info(item, key_categories)

            # Analyze breakdown structure
            breakdown_structure = self.analyze_breakdown_structure(question_info['grading_breakdown'])

            # Generate question section
            self.add_question_section(story, question_info, breakdown_structure)

            # Add space between questions
            story.append(Spacer(1, 0.4 * inch))

        # Build PDF
        doc.build(story)
        print(f"PDF generated successfully: {filename}")
        return filename

    def add_question_section(self, story, question_info, breakdown_structure):
        """Add a complete question section to the PDF"""
        # Question header (French)
        story.append(Paragraph(f"Question : {self._escape_html(question_info['question_id'])}", self.heading_style))

        # Basic info (French labels)
        basic_info = [
            ["Sujet :", self._escape_html(question_info['topic'])],
            ["Points maximum :", str(question_info['max_points'])],
            ["Note de l'étudiant :", f"{question_info['student_score']}"],
        ]

        # Calculate percentage if possible
        if question_info['max_points'] > 0:
            percentage = (question_info['student_score'] / question_info['max_points']) * 100
            basic_info.append(["Pourcentage :", f"{percentage:.1f}%"])

        basic_table = Table(basic_info, colWidths=[1.8 * inch, 4.5 * inch])
        basic_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 0.2 * inch))

        # Horizontal line
        story.append(Paragraph("<hr/>", self.normal_style))

        # Student Answer (French)
        story.append(Paragraph("Réponse de l'étudiant :", self.subheading_style))
        # Split answer into paragraphs for better formatting
        answer_paragraphs = question_info['student_answer'].split('\n')
        for para in answer_paragraphs:
            if para.strip():  # Only add non-empty paragraphs
                story.append(Paragraph(self._escape_html(para), self.normal_style))
        story.append(Spacer(1, 0.2 * inch))

        # Horizontal line
        story.append(Paragraph("<hr/>", self.normal_style))

        # Grading Breakdown (French)
        if question_info['grading_breakdown']:
            story.append(Paragraph("Répartition de la notation :", self.heading_style))
            self.add_breakdown_table(story, question_info['grading_breakdown'], breakdown_structure)
            story.append(Spacer(1, 0.2 * inch))

            # Horizontal line
            story.append(Paragraph("<hr/>", self.normal_style))

        # Overall Feedback (French)
        story.append(Paragraph("Commentaires généraux :", self.subheading_style))
        story.append(Paragraph(self._escape_html(question_info['overall_feedback']), self.normal_style))

    def add_breakdown_table(self, story, breakdown_data, structure):
        """Add grading breakdown table with dynamic structure"""
        if not breakdown_data:
            return

        # Determine which keys to use for each column
        element_key = structure['element'][0] if structure['element'] else list(breakdown_data[0].keys())[0]
        max_points_key = structure['max_points'][0] if structure['max_points'] else self.find_key_by_type(
            breakdown_data[0], 'max_points')
        score_key = structure['score'][0] if structure['score'] else self.find_key_by_type(breakdown_data[0], 'score')
        justification_key = structure['justification'][0] if structure['justification'] else self.find_key_by_type(
            breakdown_data[0], 'justification')

        # Create table headers (French)
        headers = [
            Paragraph("<b>Critère</b>", self.normal_style),
            Paragraph("<b>Points max</b>", self.normal_style),
            Paragraph("<b>Score</b>", self.normal_style),
            Paragraph("<b>Justification</b>", self.normal_style)
        ]

        breakdown_table_data = [headers]

        # Add data rows with Paragraph objects for proper text wrapping
        for item in breakdown_data:
            row = [
                Paragraph(self._escape_html(str(item.get(element_key, ''))), self.normal_style),
                Paragraph(str(item.get(max_points_key, '')), self.normal_style),
                Paragraph(str(item.get(score_key, '')), self.normal_style),
                Paragraph(self._escape_html(str(item.get(justification_key, ''))), self.normal_style)
            ]
            breakdown_table_data.append(row)

        # Create table with adjusted column widths
        breakdown_table = Table(breakdown_table_data, colWidths=[2.0 * inch, 0.7 * inch, 0.6 * inch, 3.4 * inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(breakdown_table)

    def find_key_by_type(self, item, key_type):
        """Fallback method to find keys by value type"""
        for key, value in item.items():
            if key_type == 'max_points' and isinstance(value, (int, float)) and value > 0:
                return key
            elif key_type == 'score' and isinstance(value, (int, float)):
                return key
            elif key_type == 'justification' and isinstance(value, str) and len(value) > 20:
                return key
        return list(item.keys())[0] if item else "Unknown"


# Usage examples with different JSON structures
def test_with_various_structures(data, output_path="myreport.pdf"):
    generator = SmartPDFGenerator()
    return generator.generate_pdf(data, output_path)


if __name__ == "__main__":
    data = [{
        'q_id': 'Problem 1',
        'subject_area': 'Mathematics',
        'max_marks': 10,
        'response': 'The answer is 42',
        'evaluation_criteria': [
            {
                'criterion': 'Correct answer',
                'max_score': 5,
                'points_awarded': 5,
                'comments': 'Correct solution provided'
            }
        ],
        'final_score': 5,
        'general_comments': 'Well done!'
    }]
    test_with_various_structures(data, "myreport.pdf")