"""Merge Router - PDF merge endpoint"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
from backend.services import PDFService

router = APIRouter(prefix="/api/merge", tags=["merge"])

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

@router.post("/merge-pdfs")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    """Merge multiple PDF files"""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDF files required")
    
    upload_id = uid()
    pdf_paths = []
    output_path = OUTPUTS / f"{upload_id}_merged.pdf"
    
    try:
        # Save all uploaded files
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files allowed")
            
            file_id = uid()
            pdf_path = UPLOADS / f"{file_id}.pdf"
            content = await file.read()
            
            with open(pdf_path, "wb") as f:
                f.write(content)
            
            pdf_paths.append(str(pdf_path))
        
        # Merge PDFs
        merged_data = PDFService.merge_pdfs(pdf_paths)
        
        with open(output_path, "wb") as f:
            f.write(merged_data)
        
        return {
            "status": "success",
            "file_id": upload_id,
            "file_count": len(files),
            "output_size": output_path.stat().st_size
        }
    except Exception as e:
        cleanup(output_path, *pdf_paths)
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")
    finally:
        cleanup(*pdf_paths)

@router.get("/download/{file_id}")
async def download_merged(file_id: str):
    """Download merged PDF"""
    output_path = OUTPUTS / f"{file_id}_merged.pdf"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_path, filename=f"merged_{file_id}.pdf")
