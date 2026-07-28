"""
Seed Document Generator — creates 4 realistic demo PDFs for the hackathon demo.
Uses reportlab if available, otherwise falls back to fpdf2.

Run: python generate_seeds.py
Output: demo/ folder with 4 PDF files
"""
import os
import sys

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(DEMO_DIR, exist_ok=True)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    USE_REPORTLAB = True
except ImportError:
    USE_REPORTLAB = False

if not USE_REPORTLAB:
    try:
        from fpdf import FPDF
        USE_FPDF = True
    except ImportError:
        USE_FPDF = False
else:
    USE_FPDF = False


# =========================================================
# SEED 1: Python for Data Science Certification
# =========================================================
def create_python_cert():
    path = os.path.join(DEMO_DIR, "python_data_science_cert.pdf")
    if USE_REPORTLAB:
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        blue = HexColor("#1a56db")
        gold = HexColor("#d97706")

        title_style = ParagraphStyle("title", parent=styles["Normal"], fontSize=28, textColor=blue, alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
        sub_style   = ParagraphStyle("sub",   parent=styles["Normal"], fontSize=13, textColor=HexColor("#374151"), alignment=TA_CENTER, spaceAfter=4)
        body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=11, textColor=HexColor("#1f2937"), alignment=TA_CENTER, spaceAfter=4)
        name_style  = ParagraphStyle("name",  parent=styles["Normal"], fontSize=22, textColor=HexColor("#111827"), alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
        detail_style= ParagraphStyle("detail",parent=styles["Normal"], fontSize=10, textColor=HexColor("#6b7280"), alignment=TA_CENTER, spaceAfter=4)

        content = [
            Spacer(1, 1*cm),
            Paragraph("CERTIFICATE OF COMPLETION", title_style),
            HRFlowable(width="80%", thickness=2, color=gold, spaceAfter=12, spaceBefore=12),
            Paragraph("This is to certify that", body_style),
            Spacer(1, 0.3*cm),
            Paragraph("Arjun Mehta", name_style),
            Spacer(1, 0.3*cm),
            Paragraph("has successfully completed the course", body_style),
            Spacer(1, 0.3*cm),
            Paragraph("<b>Python for Data Science &amp; Machine Learning Bootcamp</b>", sub_style),
            Spacer(1, 0.5*cm),
            Paragraph("Duration: 42 hours | Score: 94.5% | Grade: Distinction", detail_style),
            Spacer(1, 0.5*cm),
            Paragraph("Skills covered: Python, NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn,<br/>Machine Learning, Data Visualization, Statistical Analysis, Jupyter Notebooks", detail_style),
            Spacer(1, 1*cm),
            HRFlowable(width="60%", thickness=1, color=HexColor("#d1d5db"), spaceAfter=12, spaceBefore=12),
            Paragraph("Issued by: <b>Coursera | DeepLearning.AI</b>", detail_style),
            Paragraph("Date of Completion: <b>March 15, 2023</b>", detail_style),
            Paragraph("Certificate ID: DL-PY-2023-09847", detail_style),
        ]
        doc.build(content)
        print(f"Created: {path}")
    else:
        _write_text_pdf(path, "CERTIFICATE OF COMPLETION\n\nThis certifies that\n\nArjun Mehta\n\nhas successfully completed\n\nPython for Data Science & Machine Learning Bootcamp\n\nIssued by: Coursera | DeepLearning.AI\nDate: March 15, 2023\nSkills: Python, NumPy, Pandas, Matplotlib, Scikit-learn, Machine Learning\nCertificate ID: DL-PY-2023-09847\nScore: 94.5% | Grade: Distinction")


# =========================================================
# SEED 2: Machine Learning Project Report
# =========================================================
def create_ml_project():
    path = os.path.join(DEMO_DIR, "sentiment_analysis_project.pdf")
    if USE_REPORTLAB:
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.5*cm, rightMargin=2.5*cm)
        styles = getSampleStyleSheet()
        purple = HexColor("#7c3aed")

        h1 = ParagraphStyle("h1", parent=styles["Normal"], fontSize=20, textColor=purple, spaceAfter=8, fontName="Helvetica-Bold")
        h2 = ParagraphStyle("h2", parent=styles["Normal"], fontSize=13, textColor=HexColor("#374151"), spaceAfter=6, fontName="Helvetica-Bold")
        body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, textColor=HexColor("#1f2937"), spaceAfter=6, leading=16)
        meta = ParagraphStyle("meta", parent=styles["Normal"], fontSize=9, textColor=HexColor("#6b7280"), spaceAfter=4)

        content = [
            Paragraph("Sentiment Analysis on Social Media Data", h1),
            Paragraph("Machine Learning Capstone Project Report", h2),
            HRFlowable(width="100%", thickness=1, color=purple, spaceAfter=8, spaceBefore=4),
            Paragraph("Author: Arjun Mehta | Roll No: 21CS045 | B.Tech CSE — 4th Year", meta),
            Paragraph("Institution: National Institute of Technology, Trichy | Date: November 2024", meta),
            Spacer(1, 0.5*cm),

            Paragraph("Abstract", h2),
            Paragraph("This project implements a sentiment analysis pipeline on Twitter/X social media data using Natural Language Processing (NLP) and deep learning techniques. The model achieves 89.3% accuracy on a balanced dataset of 50,000 tweets, outperforming the baseline VADER lexicon approach by 12.4 percentage points.", body),
            Spacer(1, 0.3*cm),

            Paragraph("Technologies Used", h2),
            Paragraph("Python · TensorFlow · Keras · BERT (bert-base-uncased) · Hugging Face Transformers · NLTK · SpaCy · Pandas · NumPy · Matplotlib · Scikit-learn · Twitter API v2 · Google Colab", body),
            Spacer(1, 0.3*cm),

            Paragraph("Methodology", h2),
            Paragraph("1. Data Collection: Scraped 75,000 tweets using Twitter API v2 across 5 categories (positive, negative, neutral, sarcastic, mixed).<br/>2. Preprocessing: Tokenization, stop-word removal, lemmatization using SpaCy.<br/>3. Model: Fine-tuned BERT transformer with custom classification head (3-class output).<br/>4. Training: AdamW optimizer, learning rate 2e-5, batch size 32, 5 epochs on T4 GPU.<br/>5. Evaluation: Accuracy 89.3%, F1-score 0.887, AUC-ROC 0.94.", body),
            Spacer(1, 0.3*cm),

            Paragraph("Results", h2),
            Paragraph("Final model accuracy: <b>89.3%</b> on held-out test set.<br/>The project was evaluated as part of the 6th semester Machine Learning course under Dr. Priya Sundarajan, with a grade of <b>A+ (9.5/10)</b>.", body),
        ]
        doc.build(content)
        print(f"Created: {path}")
    else:
        _write_text_pdf(path, "Sentiment Analysis on Social Media Data\nMachine Learning Capstone Project Report\n\nAuthor: Arjun Mehta | B.Tech CSE 4th Year\nInstitution: NIT Trichy | Date: November 2024\n\nAbstract:\nThis project implements sentiment analysis on Twitter data using BERT.\nAccuracy: 89.3% | Grade: A+ (9.5/10)\n\nTechnologies: Python, TensorFlow, BERT, Hugging Face, NLP, Pandas, Scikit-learn\n\nMethodology: Data collection via Twitter API, BERT fine-tuning, AdamW optimizer")


# =========================================================
# SEED 3: Data Analytics Internship Offer Letter
# =========================================================
def create_internship_letter():
    path = os.path.join(DEMO_DIR, "data_analytics_internship_offer.pdf")
    if USE_REPORTLAB:
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.5*cm, rightMargin=2.5*cm)
        styles = getSampleStyleSheet()
        green = HexColor("#059669")

        h1 = ParagraphStyle("h1", parent=styles["Normal"], fontSize=16, textColor=HexColor("#111827"), spaceAfter=4, fontName="Helvetica-Bold")
        company = ParagraphStyle("company", parent=styles["Normal"], fontSize=18, textColor=green, spaceAfter=2, fontName="Helvetica-Bold")
        body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, textColor=HexColor("#1f2937"), spaceAfter=8, leading=18)
        small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, textColor=HexColor("#6b7280"), spaceAfter=4)

        content = [
            Paragraph("DataSpark Analytics Pvt. Ltd.", company),
            Paragraph("12th Floor, Prestige Tech Park, Outer Ring Road, Bangalore — 560103", small),
            Paragraph("CIN: U72200KA2018PTC110234 | HR: hr@dataspark.in", small),
            HRFlowable(width="100%", thickness=1, color=green, spaceAfter=12, spaceBefore=8),
            Paragraph("INTERNSHIP OFFER LETTER", h1),
            Paragraph("Ref: DSA/HR/INT/2025/0183 | Date: January 12, 2025", small),
            Spacer(1, 0.4*cm),
            Paragraph("Dear Arjun Mehta,", body),
            Paragraph("We are pleased to extend this offer of internship at <b>DataSpark Analytics Pvt. Ltd.</b> for the position of <b>Data Analytics Intern</b> in the Business Intelligence & Data Engineering team.", body),
            Paragraph("<b>Internship Details:</b>", body),
            Paragraph(
                "• <b>Role:</b> Data Analytics Intern (Business Intelligence)<br/>"
                "• <b>Duration:</b> 6 months (February 3, 2025 — August 2, 2025)<br/>"
                "• <b>Stipend:</b> ₹25,000/month<br/>"
                "• <b>Location:</b> Bangalore (Hybrid — 3 days onsite)<br/>"
                "• <b>Reporting to:</b> Ms. Sneha Krishnamurthy, Lead Data Analyst",
                body
            ),
            Paragraph("<b>Responsibilities:</b>", body),
            Paragraph(
                "You will work on building and maintaining Power BI dashboards, writing complex SQL queries for data extraction, "
                "performing EDA on client datasets using Python (Pandas, NumPy), and supporting the ML team with feature engineering "
                "and data pipeline automation using Apache Airflow.",
                body
            ),
            Paragraph("<b>Required Skills:</b> Python · SQL · Power BI · Pandas · NumPy · Machine Learning basics · Excel · Tableau", body),
            Spacer(1, 0.5*cm),
            Paragraph("We look forward to having you as part of our team.", body),
            Paragraph("Warm regards,", body),
            Spacer(1, 0.3*cm),
            Paragraph("<b>Rohit Sharma</b><br/>Head of Human Resources<br/>DataSpark Analytics Pvt. Ltd.", body),
        ]
        doc.build(content)
        print(f"Created: {path}")
    else:
        _write_text_pdf(path, "DataSpark Analytics Pvt. Ltd.\nINTERNSHIP OFFER LETTER\n\nDear Arjun Mehta,\n\nWe are pleased to offer you the position of Data Analytics Intern.\n\nRole: Data Analytics Intern\nDuration: February 3, 2025 — August 2, 2025\nStipend: Rs 25,000/month\nLocation: Bangalore (Hybrid)\n\nSkills Required: Python, SQL, Power BI, Pandas, Machine Learning\n\nRohit Sharma\nHead of HR, DataSpark Analytics")


# =========================================================
# SEED 4: Smart India Hackathon Achievement
# =========================================================
def create_hackathon_award():
    path = os.path.join(DEMO_DIR, "smart_india_hackathon_winner.pdf")
    if USE_REPORTLAB:
        doc = SimpleDocTemplate(path, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
        styles = getSampleStyleSheet()
        amber = HexColor("#d97706")
        blue = HexColor("#1d4ed8")

        title_style = ParagraphStyle("title", parent=styles["Normal"], fontSize=26, textColor=blue, alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
        sub_style   = ParagraphStyle("sub",   parent=styles["Normal"], fontSize=14, textColor=HexColor("#374151"), alignment=TA_CENTER, spaceAfter=4)
        body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=11, textColor=HexColor("#1f2937"), alignment=TA_CENTER, spaceAfter=4)
        name_style  = ParagraphStyle("name",  parent=styles["Normal"], fontSize=22, textColor=HexColor("#111827"), alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
        detail_style= ParagraphStyle("detail",parent=styles["Normal"], fontSize=10, textColor=HexColor("#6b7280"), alignment=TA_CENTER, spaceAfter=4)

        content = [
            Spacer(1, 0.5*cm),
            Paragraph("GOVERNMENT OF INDIA", detail_style),
            Paragraph("Ministry of Education | Innovation Cell", detail_style),
            Spacer(1, 0.3*cm),
            Paragraph("SMART INDIA HACKATHON 2024", title_style),
            HRFlowable(width="70%", thickness=3, color=amber, spaceAfter=12, spaceBefore=12),
            Paragraph("WINNER — 1st Prize", ParagraphStyle("winner", parent=styles["Normal"], fontSize=16, textColor=amber, alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")),
            Spacer(1, 0.3*cm),
            Paragraph("This certificate is proudly awarded to", body_style),
            Spacer(1, 0.2*cm),
            Paragraph("Arjun Mehta", name_style),
            Paragraph("Team: NIT Trichy — CodeCrafters", detail_style),
            Spacer(1, 0.4*cm),
            Paragraph("Problem Statement: AI-Powered Disaster Response Coordination System", sub_style),
            Paragraph("PS Code: SIH2024-MHA-0847 | Nodal Center: IIT Bombay", detail_style),
            Spacer(1, 0.5*cm),
            Paragraph("Project used: Python · FastAPI · TensorFlow · Computer Vision · NLP · Geospatial Analysis (GDAL) · React.js · PostgreSQL", detail_style),
            Spacer(1, 0.5*cm),
            HRFlowable(width="60%", thickness=1, color=HexColor("#d1d5db"), spaceAfter=12, spaceBefore=12),
            Paragraph("Prize: ₹1,00,000 | Date: December 8–9, 2024", detail_style),
            Paragraph("Evaluated by: DRDO · NDMA · IIT Bombay faculty panel", detail_style),
        ]
        doc.build(content)
        print(f"Created: {path}")
    else:
        _write_text_pdf(path, "SMART INDIA HACKATHON 2024\nGovernment of India — Ministry of Education\n\nWINNER — 1st Prize\n\nAwarded to: Arjun Mehta\nTeam: NIT Trichy CodeCrafters\n\nProject: AI-Powered Disaster Response Coordination System\nPrize: Rs 1,00,000\nDate: December 8-9, 2024\n\nSkills: Python, TensorFlow, Computer Vision, NLP, React.js, PostgreSQL")



def _stamp_synthetic(path):
    """Make every generated fixture unmistakably synthetic."""
    if not os.path.exists(path):
        return
    try:
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import Color
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError("Install demo/requirements.txt before regenerating demo PDFs") from exc

    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        buffer = BytesIO()
        overlay_canvas = canvas.Canvas(buffer, pagesize=(width, height))
        overlay_canvas.setFillColor(Color(1.0, 0.78, 0.78, 1))
        overlay_canvas.setFont("Helvetica-Bold", 27)
        overlay_canvas.translate(width / 2, height / 2)
        overlay_canvas.rotate(32)
        overlay_canvas.drawCentredString(0, 0, "SYNTHETIC DEMO - NOT A REAL CREDENTIAL")
        overlay_canvas.saveState()
        overlay_canvas.rotate(-32)
        overlay_canvas.translate(-width / 2, -height / 2)
        overlay_canvas.setFillColor(Color(0.75, 0.05, 0.05, 1))
        overlay_canvas.setFont("Helvetica-Bold", 8.5)
        overlay_canvas.drawCentredString(width / 2, 10, "SYNTHETIC HACKATHON DEMO DOCUMENT - NOT VALID FOR VERIFICATION")
        overlay_canvas.restoreState()
        overlay_canvas.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
        writer.add_page(page)
    with open(path, "wb") as output:
        writer.write(output)

def _write_text_pdf(path, text):
    """Minimal fallback if neither reportlab nor fpdf2 is installed."""
    print(f"[WARNING] reportlab not installed. Writing plain text file: {path}")
    with open(path.replace(".pdf", "_PLACEHOLDER.txt"), "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    print("Generating seed demo documents...")
    create_python_cert()
    create_ml_project()
    create_internship_letter()
    create_hackathon_award()
    for filename in (
        "python_data_science_cert.pdf",
        "sentiment_analysis_project.pdf",
        "data_analytics_internship_offer.pdf",
        "smart_india_hackathon_winner.pdf",
    ):
        _stamp_synthetic(os.path.join(DEMO_DIR, filename))
    print("\nAll synthetic seed documents created in the demo/ folder.")
    print("Upload these to MemoryVerse AI to demonstrate the full pipeline!")
