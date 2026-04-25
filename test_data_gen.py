from reportlab.pdfgen import canvas

c = canvas.Canvas("dummy_resume.pdf")
c.drawString(100, 800, "John Doe - Backend Developer")
c.drawString(100, 780, "Skills: Python, Flask, SQL, Git")
c.drawString(100, 760, "Experience: Built REST APIs.")
c.save()

c2 = canvas.Canvas("dummy_jd.pdf")
c2.drawString(100, 800, "Job Description: Backend Engineer")
c2.drawString(100, 780, "Requirements: Python, Flask, Docker, AWS, React")
c2.drawString(100, 760, "Experience in cloud environments.")
c2.save()
