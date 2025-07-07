from fastapi import FastAPI, Response
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from io import BytesIO
import threading
import os

app = FastAPI()
lock = threading.Lock()
COUNTER_FILE = "counter.txt"
BACKGROUND_IMAGE = "Bills of exchange 1_page-0001.jpg"  # ✅ Make sure this file exists in the same folder

class BillInfo(BaseModel):
    date: str
    amount: str
    due_date: str
    pay_at: str
    exporter_bank: str
    
    fcy_amount: str
    fcy_words: str
    invoice_number: str
    invoice_date: str
    exporter_company: str
    buyer_name: str
    buyer_address: str

def get_next_counter():
    with lock:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return 1
        with open(COUNTER_FILE, "r+") as f:
            count = int(f.read())
            f.seek(0)
            f.write(str(count + 1))
            f.truncate()
            return count

@app.post("/generate-pdf/")
async def generate_pdf(info: BillInfo):
    pdf_number = get_next_counter()
    filename = f"bill_of_exchange_{pdf_number}.pdf"

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ✅ Try loading the image and return real error if it fails
    try:
        img = ImageReader(BACKGROUND_IMAGE)
        c.drawImage(img, 0, 0, width=width, height=height)
    except Exception as e:
        return Response(
            content=f"Image load error: {str(e)}",
            media_type="text/plain",
            status_code=500
        )

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(black)

    # 🖊️ Draw dynamic fields on top of the image
    c.drawString(140, 615, info.date)
    c.drawString(150, 565, info.amount)
    c.drawString(250, 530, info.due_date)
    c.drawString(280, 485, info.pay_at)
    c.drawString(250, 465, info.exporter_bank)
    c.drawString(250, 410, info.fcy_amount)
    c.drawString(150,395, info.fcy_words)
    c.drawString(225, 360, info.invoice_number)
    c.drawString(350, 360, info.invoice_date)
    c.drawString(310, 310, info.exporter_company)
    c.drawString(250, 140, info.buyer_name)
    c.drawString(250, 125, info.buyer_address)

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
