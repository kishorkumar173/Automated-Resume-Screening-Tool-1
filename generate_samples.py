"""
=============================================================================
Script: generate_samples.py
Description: Automatically generates 5 realistic, industry-standard synthetic
             resumes in PDF and DOCX formats for testing and simulation.
=============================================================================
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import docx
from docx.shared import Pt, Inches, RGBColor


RESUMES_DIR = os.path.join(os.path.dirname(__file__), "resumes")
os.makedirs(RESUMES_DIR, exist_ok=True)


def create_pdf_resume(filename: str, name: str, contact: dict, summary: str, skills: list, experiences: list, education: str):
    """Generates an ATS-compliant PDF resume with clean typography using ReportLab."""
    filepath = os.path.join(RESUMES_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    story = []

    # Name & Contact Header
    story.append(Paragraph(name, title_style))
    contact_line = f"{contact.get('email')} | {contact.get('phone')} | {contact.get('location')} | {contact.get('linkedin')}"
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 4))

    # Core Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", heading_style))
    skills_text = " • ".join(skills)
    story.append(Paragraph(f"<b>Key Proficiencies:</b> {skills_text}", body_style))
    story.append(Spacer(1, 4))

    # Work Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))
    for exp in experiences:
        role_line = f"<b>{exp['role']}</b> — <i>{exp['company']}</i> ({exp['period']})"
        story.append(Paragraph(role_line, body_style))
        for bullet in exp['bullets']:
            story.append(Paragraph(f"&bull; {bullet}", body_style))
        story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    story.append(Paragraph(education, body_style))

    doc.build(story)
    print(f"  [+] Generated PDF: {filename}")


def create_docx_resume(filename: str, name: str, contact: dict, summary: str, skills: list, experiences: list, education: str):
    """Generates an ATS-compliant Word DOCX resume using python-docx."""
    filepath = os.path.join(RESUMES_DIR, filename)
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

    # Name Header
    name_para = doc.add_paragraph()
    run = name_para.add_run(name)
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 41, 59)
    name_para.paragraph_format.space_after = Pt(2)

    # Contact line
    contact_para = doc.add_paragraph()
    contact_text = f"{contact.get('email')} | {contact.get('phone')} | {contact.get('location')} | {contact.get('linkedin')}"
    c_run = contact_para.add_run(contact_text)
    c_run.font.size = Pt(9.5)
    c_run.font.color.rgb = RGBColor(71, 85, 105)
    contact_para.paragraph_format.space_after = Pt(10)

    # Helper function for section headings
    def add_section_header(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title.upper())
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 23, 42)

    # Professional Summary
    add_section_header("Professional Summary")
    doc.add_paragraph(summary).paragraph_format.space_after = Pt(6)

    # Skills
    add_section_header("Technical Skills")
    skills_para = doc.add_paragraph()
    skills_para.add_run("Skills & Tools: ").bold = True
    skills_para.add_run(", ".join(skills))
    skills_para.paragraph_format.space_after = Pt(6)

    # Experience
    add_section_header("Work Experience")
    for exp in experiences:
        exp_header = doc.add_paragraph()
        r1 = exp_header.add_run(f"{exp['role']} | {exp['company']}")
        r1.bold = True
        exp_header.add_run(f" ({exp['period']})").italic = True
        exp_header.paragraph_format.space_after = Pt(2)
        
        for bullet in exp['bullets']:
            bp = doc.add_paragraph(bullet, style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)

    # Education
    add_section_header("Education")
    doc.add_paragraph(education).paragraph_format.space_after = Pt(4)

    doc.save(filepath)
    print(f"  [+] Generated DOCX: {filename}")


def generate_all_sample_resumes():
    """Populates resumes directory with 5 diverse candidates."""
    print("\n--- Generating Industry-Standard Sample Resumes ---")

    # Candidate 1: John Doe (Senior Python & ML Engineer - Expected High Match)
    create_pdf_resume(
        filename="resume_john_doe_senior_python.pdf",
        name="John Doe",
        contact={
            "email": "john.doe.dev@gmail.com",
            "phone": "+1 (555) 234-5678",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoepython"
        },
        summary="Senior Python Engineer with 5+ years of experience specializing in Machine Learning pipelines, backend REST APIs with FastAPI, and cloud deployment. Proven track record in Scikit-learn, Pandas, Docker, and PostgreSQL.",
        skills=[
            "Python", "Machine Learning", "Scikit-learn", "Pandas", "NumPy", 
            "FastAPI", "SQL", "PostgreSQL", "Docker", "AWS", "Git", "CI/CD", "NLP"
        ],
        experiences=[
            {
                "role": "Lead Python & ML Developer",
                "company": "Cognitive Solutions Inc",
                "period": "2021 – Present",
                "bullets": [
                    "Engineered asynchronous microservices using FastAPI and Docker, handling 15M daily requests.",
                    "Designed automated machine learning pipelines with Scikit-learn and Pandas for text classification and NLP.",
                    "Optimized SQL queries and PostgreSQL database indexing, reducing query response latency by 42%.",
                    "Integrated CI/CD pipelines via GitHub Actions and deployed containerized apps to AWS ECS."
                ]
            },
            {
                "role": "Software Engineer (Python/Data)",
                "company": "DataSphere Analytics",
                "period": "2019 – 2021",
                "bullets": [
                    "Built feature engineering pipelines with NumPy and Pandas for predictive customer retention models.",
                    "Developed RESTful APIs with Flask and Redis caching to serve model inference endpoints."
                ]
            }
        ],
        education="B.S. in Computer Science — University of California, Berkeley (2019)"
    )

    # Candidate 2: Priya Sharma (Data Analyst - Expected Medium Match)
    create_pdf_resume(
        filename="resume_priya_sharma_data_analyst.pdf",
        name="Priya Sharma",
        contact={
            "email": "priya.sharma.analytics@outlook.com",
            "phone": "+1 (555) 876-5432",
            "location": "Chicago, IL",
            "linkedin": "linkedin.com/in/priyasharma-data"
        },
        summary="Data Analyst with 3 years of experience in data visualization, SQL queries, business intelligence, and Python data manipulation. Proficient in Tableau, Power BI, Excel, Pandas, and statistics.",
        skills=[
            "Python", "Pandas", "NumPy", "SQL", "Tableau", "Power BI", 
            "Excel", "Data Visualization", "Statistics", "Git", "Machine Learning"
        ],
        experiences=[
            {
                "role": "Business Data Analyst",
                "company": "Apex Financial Group",
                "period": "2022 – Present",
                "bullets": [
                    "Created interactive executive dashboards using Tableau and Power BI for tracking KPIs.",
                    "Extracted and transformed complex datasets using SQL and Python Pandas.",
                    "Conducted A/B testing and statistical analysis to improve conversion rates by 18%."
                ]
            }
        ],
        education="B.S. in Statistics and Data Analytics — University of Illinois (2022)"
    )

    # Candidate 3: Michael Brown (Java Backend Developer - Partial Match)
    create_pdf_resume(
        filename="resume_michael_brown_java_backend.pdf",
        name="Michael Brown",
        contact={
            "email": "michael.brown.tech@gmail.com",
            "phone": "+1 (555) 432-1098",
            "location": "Austin, TX",
            "linkedin": "linkedin.com/in/michaelbrown-backend"
        },
        summary="Backend Software Engineer with 4 years building enterprise microservices using Java, Spring Boot, PostgreSQL, and Docker. Experience with AWS cloud infrastructure and CI/CD automation.",
        skills=[
            "Java", "Spring Boot", "SQL", "PostgreSQL", "Docker", "AWS", 
            "Git", "CI/CD", "Redis", "Microservices", "REST API", "Python"
        ],
        experiences=[
            {
                "role": "Backend Java Engineer",
                "company": "Fintech Enterprise Corp",
                "period": "2020 – Present",
                "bullets": [
                    "Developed high-throughput transaction microservices using Java and Spring Boot.",
                    "Containerized backend applications using Docker and orchestrated deployments on AWS EKS.",
                    "Wrote automated unit tests and maintained CI/CD pipelines in GitLab."
                ]
            }
        ],
        education="B.S. in Software Engineering — University of Texas at Austin (2020)"
    )

    # Candidate 4: Alex Smith (Frontend Developer - Low Match / DOCX)
    create_docx_resume(
        filename="resume_alex_smith_frontend_dev.docx",
        name="Alex Smith",
        contact={
            "email": "alex.smith.ui@yahoo.com",
            "phone": "+1 (555) 321-7654",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/alexsmith-frontend"
        },
        summary="Creative Frontend Developer with 3+ years experience building dynamic, responsive single-page web applications using React, TypeScript, JavaScript, HTML, and CSS.",
        skills=[
            "JavaScript", "TypeScript", "React.js", "HTML", "CSS", 
            "Node.js", "Git", "Webpack", "Tailwind CSS", "REST API"
        ],
        experiences=[
            {
                "role": "Frontend Web Developer",
                "company": "PixelCraft Studios",
                "period": "2021 – Present",
                "bullets": [
                    "Developed responsive web interfaces using React and modern component libraries.",
                    "Collaborated with UI/UX designers to translate Figma mockups into production-ready frontends.",
                    "Integrated RESTful API endpoints and optimized client-side performance."
                ]
            }
        ],
        education="B.A. in Interactive Media — New York University (2021)"
    )

    # Candidate 5: Emily Clark (Digital Marketing Specialist - Reject / DOCX)
    create_docx_resume(
        filename="resume_emily_clark_digital_marketing.docx",
        name="Emily Clark",
        contact={
            "email": "emily.clark.marketing@gmail.com",
            "phone": "+1 (555) 987-6543",
            "location": "Seattle, WA",
            "linkedin": "linkedin.com/in/emilyclark-growth"
        },
        summary="Results-oriented Digital Marketing Specialist with 4 years driving brand growth through SEO, Google Ads, content marketing campaigns, and social media analytics.",
        skills=[
            "Search Engine Optimization (SEO)", "Google Ads", "Content Marketing", 
            "Social Media Management", "Email Marketing", "Copywriting", "Communication"
        ],
        experiences=[
            {
                "role": "Digital Marketing Strategist",
                "company": "Global Brand Marketing",
                "period": "2020 – Present",
                "bullets": [
                    "Managed multi-channel paid acquisition campaigns generating $2.4M in pipeline.",
                    "Conducted keyword research and optimized on-page SEO to increase organic search traffic by 65%.",
                    "Collaborated with creative teams to produce branded content and social media assets."
                ]
            }
        ],
        education="B.A. in Marketing & Communications — University of Washington (2020)"
    )

    print("--- Successfully Created 5 Sample Resumes in 'resumes/' ---\n")


if __name__ == "__main__":
    generate_all_sample_resumes()
