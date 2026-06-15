"""Split Router - PDF split endpoint"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
from backend.services import PDFService
from pypdf import PdfReader

router = APIRouter(prefix="/api/split", tags=["split"])

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

@router.post("/get-pages")
async def get_pages(file: UploadFile = File(...)):
    """Get total pages in PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        content = await file.read()
        reader = PdfReader(file.file)
        file.file.seek(0)
        reader = PdfReader(file.file)
        pages = len(reader.pages)
        
        return {"pages": pages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

@router.post("/split-pdf")
async def split_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(...),
    end_page: int = Form(...)
):
    """Split PDF by page range"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    output_path = OUTPUTS / f"{upload_id}_split.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Validate page range
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            raise HTTPException(status_code=400, detail="Invalid page range")
        
        # Split PDF
        split_data = PDFService.split_pdf(str(input_path), start_page, end_page)
        
        with open(output_path, "wb") as f:
            f.write(split_data)
        
        return {
            "status": "success",
            "file_id": upload_id,
            "total_pages": total_pages,
            "extracted_pages": end_page - start_page + 1,
            "output_size": output_path.stat().st_size
        }
    except Exception as e:
        cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Split failed: {str(e)}")

@router.get("/download/{file_id}")
async def download_split(file_id: str):
    """Download split PDF"""
    output_path = OUTPUTS / f"{file_id}_split.pdf"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_path, filename=f"split_{file_id}.pdf")
