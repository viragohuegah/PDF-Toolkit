"""Watermark Router - PDF watermarking endpoint"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

router = APIRouter(prefix="/api/watermark", tags=["watermark"])

BASE = Path(__file__).parent.parent.parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"

def uid():
    return str(uuid.uuid4())

def cleanup(*paths):
    for p in paths:
        try:
            if p and Path(p).exists():
                Path(p).unlink()
        except:
            pass

@router.post("/add-watermark")
async def add_watermark(
    file: UploadFile = File(...),
    text: str = Form("WATERMARK"),
    opacity: float = Form(0.3),
    color: str = Form("red")
):
    """Add text watermark to PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    if opacity < 0 or opacity > 1:
        raise HTTPException(status_code=400, detail="Opacity must be between 0 and 1")

    color_map = {
        "red": Color(1, 0, 0),
        "gray": Color(0.45, 0.45, 0.45),
        "grey": Color(0.45, 0.45, 0.45),
        "black": Color(0, 0, 0),
        "blue": Color(0, 0.25, 1),
    }
    selected_color = color_map.get(color.lower())
    if selected_color is None:
        raise HTTPException(status_code=400, detail="Color must be red, gray, black, or blue")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    output_path = OUTPUTS / f"{upload_id}_watermarked.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=(width, height))
            font_size = max(36, min(width, height) / 9)
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(selected_color)
            c.setFillAlpha(opacity)

            c.saveState()
            c.translate(width / 2, height / 2)
            c.rotate(45)
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(-text_width / 2, -font_size / 3, text)
            c.restoreState()
            c.save()
            watermark_buffer.seek(0)

            watermark_pdf = PdfReader(watermark_buffer)
            watermark_page = watermark_pdf.pages[0]
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return {
            "status": "success",
            "file_id": upload_id,
            "filename": file.filename,
            "watermark_text": text,
            "opacity": opacity,
            "color": color
        }
    except Exception as e:
        cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Watermarking failed: {str(e)}")

@router.get("/download/{file_id}")
async def download_watermarked(file_id: str):
    """Download watermarked PDF"""
    output_path = OUTPUTS / f"{file_id}_watermarked.pdf"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_path, filename=f"watermarked_{file_id}.pdf")
