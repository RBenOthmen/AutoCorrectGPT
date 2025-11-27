import json
from pdf_generator import SmartPDFGenerator

# Test with complex, long text similar to real student answers
test_data = {
    "corrections": [
        {
            "question_id": "Question 1",
            "topic": "Calcul différentiel - Dérivées",
            "max_points": 20,
            "student_score": 16,
            "student_answer": """Soit f(x) = x^3 - 3x^2 + 5x - 2.

Pour calculer f'(x), j'applique la règle de dérivation terme par terme :
- La dérivée de x^3 est 3x^2 (règle de puissance)
- La dérivée de -3x^2 est -6x (règle de puissance avec coefficient)
- La dérivée de 5x est 5 (dérivée d'une fonction linéaire)
- La dérivée de -2 est 0 (dérivée d'une constante)

Donc f'(x) = 3x^2 - 6x + 5.

Pour résoudre f'(x) = 0, je pose 3x^2 - 6x + 5 = 0.
J'utilise le discriminant : Δ = b² - 4ac = (-6)² - 4(3)(5) = 36 - 60 = -24.
Comme Δ < 0, il n'y a pas de solution réelle.

Pour f'(2), je remplace x par 2 :
f'(2) = 3(2)² - 6(2) + 5 = 12 - 12 + 5 = 5.
Cela signifie que la pente de la tangente en x=2 est 5.""",
            "grading_breakdown": [
                {
                    "element": "Calcul de la dérivée f'(x)",
                    "max_points": 6,
                    "score": 6,
                    "justification": "La dérivée f'(x) = 3x² - 6x + 5 est parfaitement calculée. L'étudiant a correctement appliqué la règle de puissance à chaque terme."
                },
                {
                    "element": "Explication des règles de dérivation",
                    "max_points": 4,
                    "score": 3,
                    "justification": "L'étudiant mentionne la règle de puissance et explique chaque étape, mais ne cite pas explicitement le principe de linéarité de la dérivation."
                },
                {
                    "element": "Résolution de f'(x) = 0",
                    "max_points": 5,
                    "score": 4,
                    "justification": "Le calcul du discriminant est correct (Δ = -24), et la conclusion qu'il n'y a pas de solution réelle est juste. Cependant, l'étudiant aurait pu mentionner que cela signifie que f n'a pas de point critique."
                },
                {
                    "element": "Calcul de f'(2) et interprétation",
                    "max_points": 5,
                    "score": 3,
                    "justification": "Le calcul f'(2) = 5 est correct. L'interprétation comme pente de la tangente est bonne, mais l'étudiant aurait pu ajouter que cela indique une fonction croissante en ce point."
                }
            ],
            "overall_feedback": "Excellent travail dans l'ensemble ! Les calculs sont précis et bien présentés. Pour améliorer, pensez à toujours mentionner les propriétés théoriques (linéarité, interprétation géométrique complète) en plus des calculs."
        }
    ]
}

print("Testing PDF generation with complex data...")
print("\nGenerating PDF...")

generator = SmartPDFGenerator()
output_file = "reports/complex_test_report.pdf"
generator.generate_pdf(test_data, output_file)
print(f"\n✓ PDF generated successfully: {output_file}")
print("\nPlease open the PDF to verify:")
print("  - Text wrapping in tables")
print("  - Paragraph formatting in student answers")
print("  - Special characters (é, à, ', etc.)")
print("  - Overall layout and readability")
