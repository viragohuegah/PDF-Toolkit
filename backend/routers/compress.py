"""Compress Router - PDF compression endpoint"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
from backend.services import GhostscriptService

router = APIRouter(prefix="/api/compress", tags=["compress"])

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

@router.post("/compress-pdf")
async def compress_pdf(
    file: UploadFile = File(...),
    quality: str = Form("ebook")
):
    """Compress PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    output_path = OUTPUTS / f"{upload_id}_compressed.pdf"
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Check file size (max 50MB)
        if input_path.stat().st_size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Compress using Ghostscript
        GhostscriptService.compress_pdf(str(input_path), str(output_path), quality)
        
        # Get original and compressed sizes
        original_size = input_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        return {
            "status": "success",
            "file_id": upload_id,
            "filename": file.filename,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction": round(reduction, 2)
        }
    except Exception as e:
        cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")

@router.get("/download/{file_id}")
async def download_compressed(file_id: str):
    """Download compressed PDF"""
    output_path = OUTPUTS / f"{file_id}_compressed.pdf"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_path, filename=f"compressed_{file_id}.pdf")
