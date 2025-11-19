from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def build_pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    c.setFont("Helvetica", 10)

    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
        c.drawString(50, y, line)
        y -= 14

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
