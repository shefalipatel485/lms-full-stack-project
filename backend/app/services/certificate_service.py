import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_certificate_pdf(student_name: str, course_title: str, cert_number: str, issued_date: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Outer & Inner Borders
    c.setStrokeColor(colors.HexColor("#1e3a8a"))
    c.setLineWidth(6)
    c.rect(25, 25, width - 50, height - 50)

    c.setStrokeColor(colors.HexColor("#d97706"))
    c.setLineWidth(2)
    c.rect(35, 35, width - 70, height - 70)

    # Header
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 110, "CERTIFICATE OF COMPLETION")

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 155, "This is to proudly certify that")

    # Student Name
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 205, student_name)

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 250, "has successfully completed all academic requirements for the course")

    # Course Title
    c.setFillColor(colors.HexColor("#1d4ed8"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 295, course_title)

    # Footer details
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 12)
    c.drawString(70, 95, f"Certificate ID: {cert_number}")
    c.drawString(70, 75, f"Issued Date: {issued_date}")
    c.drawRightString(width - 70, 95, "Authorized Academic Director")
    c.drawRightString(width - 70, 75, "Institute Learning Management System")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
