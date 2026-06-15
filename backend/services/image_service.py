"""Image Service - Image conversion utilities"""
import io
from pathlib import Path
from PIL import Image
import fitz

class ImageService:
    @staticmethod
    def pdf_to_images(pdf_path: str, output_format: str = "png", dpi: int = 150) -> list:
        """Convert PDF pages to images"""
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num, page in enumerate(doc):
            # Render page to image with specified DPI
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img_bytes = io.BytesIO()
            
            if output_format.lower() == "png":
                img_data = pix.tobytes("png")
            else:  # jpg
                img_data = pix.tobytes("jpg")
            
            img_bytes.write(img_data)
            img_bytes.seek(0)
            images.append((f"page_{page_num + 1}.{output_format}", img_bytes.getvalue()))
        
        doc.close()
        return images

    @staticmethod
    def images_to_pdf(image_paths: list, order: list = None) -> bytes:
        """Convert multiple images to PDF"""
        images = []
        
        if order:
            image_paths = [image_paths[i] for i in order]
        
        for img_path in image_paths:
            img = Image.open(img_path)
            if img.mode == "RGBA":
                # Convert RGBA to RGB
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                images.append(rgb_img.convert("RGB"))
            else:
                images.append(img.convert("RGB"))
        
        output = io.BytesIO()
        images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_thumbnail(pdf_path: str, page_num: int = 0, size: tuple = (150, 200)) -> bytes:
        """Generate thumbnail for PDF page"""
        doc = fitz.open(pdf_path)
        page = doc[min(page_num, len(doc) - 1)]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        
        doc.close()
        return output.getvalue()
