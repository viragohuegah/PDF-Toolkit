"""
PDF Toolkit - Production Ready Web Application
FastAPI Backend with comprehensive PDF processing capabilities
"""
import os
import asyncio
import zipfile
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader, PdfWriter
from PIL import Image
import fitz
import shutil
import traceback

# Import routers
from backend.routers import (
    compress_router,
    merge_router,
    split_router,
    convert_router,
    security_router,
    watermark_router,
    preview_router,
)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Toolkit",
    description="Complete PDF processing toolkit with compression, merging, splitting, and more",
    version="1.0.0"
)

# Setup paths
BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
STATIC = BASE / "static"
FRONTEND = BASE / "frontend"

# Create directories
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if STATIC.exists():
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

if FRONTEND.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND), name="frontend")

# Include routers
app.include_router(compress_router)
app.include_router(merge_router)
app.include_router(split_router)
app.include_router(convert_router)
app.include_router(security_router)
app.include_router(watermark_router)
app.include_router(preview_router)

# Helper functions
def uid():
    """Generate unique ID"""
    return str(uuid.uuid4())

def cleanup(*paths):
    """Cleanup temporary files"""
    for p in paths:
        try:
            if p and Path(p).exists():
                Path(p).unlink()
        except:
            pass

async def save_upload(file: UploadFile, suffix: str = ".pdf"):
    """Save uploaded file"""
    upload_id = uid()
    file_path = UPLOADS / f"{upload_id}{suffix}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    index_path = FRONTEND / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>PDF Toolkit</h1><p>Welcome!</p>"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": "PDF Toolkit v1.0"}

@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "name": "PDF Toolkit API",
        "version": "1.0.0",
        "features": [
            "compress",
            "merge",
            "split",
            "pdf_to_image",
            "image_to_pdf",
            "pdf_to_text",
            "pdf_to_word",
            "protect",
            "unlock",
            "restrict_permissions",
            "watermark",
            "preview",
        ]
    }

# Cleanup task
async def cleanup_old_files():
    """Cleanup old files periodically"""
    import time
    MAX_AGE = 24 * 60 * 60  # 24 hours
    current_time = time.time()
    
    for directory in [UPLOADS, OUTPUTS]:
        if directory.exists():
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > MAX_AGE:
                        try:
                            file_path.unlink()
                        except:
                            pass

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("🚀 PDF Toolkit API started")
    print("📁 Uploads: ", UPLOADS)
    print("📁 Outputs: ", OUTPUTS)
    print("📁 Frontend: ", FRONTEND)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("🛑 PDF Toolkit API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )


@app.post("/split")
async def split_pdf(file: UploadFile = File(...)):
    input_path = save_upload(file)
    reader = PdfReader(str(input_path))
    zip_path = OUTPUTS / f"split_{uid()}.zip"

    temp_files = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        page_path = OUTPUTS / f"page_{i+1}_{uid()}.pdf"
        with open(page_path, "wb") as f:
            writer.write(f)

        temp_files.append(page_path)

    with zipfile.ZipFile(zip_path, "w") as z:
        for p in temp_files:
            z.write(p, p.name)

    cleanup(input_path, *temp_files)
    return FileResponse(zip_path, filename="split_pages.zip")


@app.post("/pdf-to-image")
async def pdf_to_image(file: UploadFile = File(...), image_format: str = Form("png")):
    input_path = save_upload(file)
    doc = fitz.open(input_path)

    zip_path = OUTPUTS / f"images_{uid()}.zip"
    image_paths = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_path = OUTPUTS / f"page_{page_index+1}.{image_format}"
        pix.save(img_path)
        image_paths.append(img_path)

    doc.close()

    with zipfile.ZipFile(zip_path, "w") as z:
        for p in image_paths:
            z.write(p, p.name)

    cleanup(input_path, *image_paths)
    return FileResponse(zip_path, filename="pdf_images.zip")


@app.post("/image-to-pdf")
async def image_to_pdf(files: list[UploadFile] = File(...)):
    images = []
    paths = []

    for file in files:
        suffix = Path(file.filename).suffix.lower()
        path = save_upload(file, suffix=suffix)
        paths.append(path)

        img = Image.open(path).convert("RGB")
        images.append(img)

    output_path = OUTPUTS / f"images_{uid()}.pdf"

    images[0].save(output_path, save_all=True, append_images=images[1:])

    cleanup(*paths)
    return FileResponse(output_path, filename="images_to_pdf.pdf")


@app.post("/pdf-to-text")
async def pdf_to_text(file: UploadFile = File(...)):
    input_path = save_upload(file)
    doc = fitz.open(input_path)

    text = ""
    for page in doc:
        text += page.get_text() + "\n"

    doc.close()

    output_path = OUTPUTS / f"text_{uid()}.txt"
    output_path.write_text(text, encoding="utf-8")

    cleanup(input_path)
    return FileResponse(output_path, filename="extracted_text.txt")


@app.post("/protect")
async def protect_pdf(file: UploadFile = File(...), password: str = Form(...)):
    input_path = save_upload(file)
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    output_path = OUTPUTS / f"protected_{uid()}.pdf"

    with open(output_path, "wb") as f:
        writer.write(f)

    cleanup(input_path)
    return FileResponse(output_path, filename="protected.pdf")


@app.post("/unlock")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    input_path = save_upload(file)
    reader = PdfReader(str(input_path))

    if reader.is_encrypted:
        reader.decrypt(password)

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    output_path = OUTPUTS / f"unlocked_{uid()}.pdf"

    with open(output_path, "wb") as f:
        writer.write(f)

    cleanup(input_path)
    return FileResponse(output_path, filename="unlocked.pdf")


@app.post("/restrict")
async def restrict_pdf(file: UploadFile = File(...), password: str = Form(...)):
    input_path = save_upload(file)
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password="",
        owner_password=password,
        permissions_flag=0
    )

    output_path = OUTPUTS / f"restricted_{uid()}.pdf"

    with open(output_path, "wb") as f:
        writer.write(f)

    cleanup(input_path)
    return FileResponse(output_path, filename="restricted.pdf")


@app.post("/watermark")
async def watermark_pdf(file: UploadFile = File(...), text: str = Form("CONFIDENTIAL")):
    input_path = save_upload(file)
    doc = fitz.open(input_path)

    for page in doc:
        rect = page.rect
        page.insert_text(
            (rect.width / 3, rect.height / 2),
            text,
            fontsize=36,
            rotate=45,
            fill=(0.6, 0.6, 0.6),
        )

    output_path = OUTPUTS / f"watermarked_{uid()}.pdf"
    doc.save(output_path)
    doc.close()

    cleanup(input_path)
    return FileResponse(output_path, filename="watermarked.pdf")


@app.post("/preview")
async def preview_pdf(file: UploadFile = File(...)):
    input_path = save_upload(file)
    doc = fitz.open(input_path)

    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))

    output_path = OUTPUTS / f"preview_{uid()}.png"
    pix.save(output_path)

    doc.close()
    cleanup(input_path)

    return FileResponse(output_path, filename="preview.png")