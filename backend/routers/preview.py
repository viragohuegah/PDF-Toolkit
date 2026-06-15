"""Preview Router - Thumbnail and preview endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import uuid
import io
from pathlib import Path
from backend.services import ImageService
import base64

router = APIRouter(prefix="/api/preview", tags=["preview"])

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

@router.post("/thumbnail")
async def get_thumbnail(file: UploadFile = File(...)):
    """Generate thumbnail for PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Generate thumbnail
        thumbnail_data = ImageService.generate_thumbnail(str(input_path), page_num=0, size=(200, 250))
        
        # Convert to base64
        base64_thumb = base64.b64encode(thumbnail_data).decode()
        
        return {
            "status": "success",
            "thumbnail": f"data:image/png;base64,{base64_thumb}",
            "filename": file.filename
        }
    except Exception as e:
        cleanup(input_path)
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")
    finally:
        cleanup(input_path)

@router.post("/preview-image")
async def get_preview_image(file: UploadFile = File(...)):
    """Get preview image for PDF as base64"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_id = uid()
    input_path = UPLOADS / f"{upload_id}.pdf"
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Generate thumbnail
        thumbnail_data = ImageService.generate_thumbnail(str(input_path), page_num=0, size=(300, 400))
        
        # Convert to base64
        base64_img = base64.b64encode(thumbnail_data).decode()
        
        return {
            "status": "success",
            "image": f"data:image/png;base64,{base64_img}"
        }
    except Exception as e:
        cleanup(input_path)
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")
    finally:
        cleanup(input_path)
