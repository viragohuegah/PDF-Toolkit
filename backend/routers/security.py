"""Security Router - PDF protection endpoints"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
from backend.services import PDFService

router = APIRouter(prefix="/api/security", tags=["security"])

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

@router.post("/protect-pdf")
async def protect_pdf(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    """Protect PDF with password"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    output_path = OUTPUTS / f"{upload_id}_protected.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Protect PDF
        protected_data = PDFService.protect_pdf(str(input_path), password)
        
        with open(output_path, "wb") as f:
            f.write(protected_data)
        
        return {
            "status": "success",
            "file_id": upload_id,
            "filename": file.filename,
            "protected": True
        }
    except Exception as e:
        cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Protection failed: {str(e)}")

@router.post("/restrict-pdf")
async def restrict_pdf(
    file: UploadFile = File(...),
    can_print: bool = Form(False),
    can_edit: bool = Form(False),
    can_copy: bool = Form(False)
):
    """Restrict PDF permissions"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    output_path = OUTPUTS / f"{upload_id}_restricted.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Restrict permissions
        restricted_data = PDFService.restrict_permissions(
            str(input_path),
            can_print=can_print,
            can_edit=can_edit,
            can_copy=can_copy
        )
        
        with open(output_path, "wb") as f:
            f.write(restricted_data)
        
        return {
            "status": "success",
            "file_id": upload_id,
            "filename": file.filename,
            "restrictions": {
                "can_print": can_print,
                "can_edit": can_edit,
                "can_copy": can_copy
            }
        }
    except Exception as e:
        cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=f"Restriction failed: {str(e)}")

@router.get("/download/{file_id}/{output_type}")
async def download_protected(file_id: str, output_type: str):
    """Download protected/unlocked/restricted PDF"""
    if output_type == "protected":
        output_path = OUTPUTS / f"{file_id}_protected.pdf"
    elif output_type == "restricted":
        output_path = OUTPUTS / f"{file_id}_restricted.pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid output type")
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(output_path, filename=f"{output_type}_{file_id}.pdf")
