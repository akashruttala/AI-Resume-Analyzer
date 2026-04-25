from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_wrapped_text(c, text, x, y, max_width):
    """Helper to wrap text and return the new y position"""
    words = text.split()
    line = ""
    for word in words:
        if c.stringWidth(line + word + " ", "Helvetica", 11) < max_width:
            line += word + " "
        else:
            c.drawString(x, y, line)
            y -= 15
            line = word + " "
    if line:
        c.drawString(x, y, line)
        y -= 20
    return y

def check_page_break(c, y, height):
    if y < 50:
        c.showPage()
        c.setFont("Helvetica", 11)
        return height - 50
    return y

def generate_report(output_path, analysis_result, suggestions, role_name):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Resume Analysis Report")
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(50, height - 70, f"Target Role: {role_name}")
    
    # Score
    c.setFont("Helvetica-Bold", 16)
    interpretation = analysis_result.get('interpretation', '')
    c.drawString(50, height - 110, f"Match Score: {analysis_result['score']}% ({interpretation})")
    
    # Matched Skills
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawString(50, height - 150, "Matched Skills:")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.darkgreen)
    matched = ", ".join(analysis_result['matched_skills']) if analysis_result['matched_skills'] else "None"
    y_pos = draw_wrapped_text(c, matched, 70, height - 170, width - 100)
    
    # Missing Skills
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos - 10, "Missing Skills:")
    y_pos -= 30
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.red)
    missing = ", ".join(analysis_result['missing_skills']) if analysis_result['missing_skills'] else "None"
    y_pos = draw_wrapped_text(c, missing, 70, y_pos, width - 100)
    
    # Sections from Gemini Structured Output
    sections = [
        ("Skill Roadmap (Priority Order):", suggestions.get('skill_roadmap', [])),
        ("Resume Rewrite Tips:", suggestions.get('resume_tips', [])),
        ("Project Suggestions:", suggestions.get('project_suggestions', []))
    ]
    
    y_pos -= 10
    
    for title, points in sections:
        y_pos = check_page_break(c, y_pos, height)
        c.setFillColor(colors.darkblue)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, title)
        y_pos -= 20
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 11)
        
        for point in points:
            y_pos = check_page_break(c, y_pos, height)
            # Add a bullet point character
            c.drawString(60, y_pos, "•")
            y_pos = draw_wrapped_text(c, point, 75, y_pos, width - 110)

    c.save()
