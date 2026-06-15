"""PDF Service - Core PDF manipulation utilities"""
import io
import uuid
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
import fitz

class PDFService:
    @staticmethod
    def merge_pdfs(pdf_paths: list) -> bytes:
        """Merge multiple PDF files"""
        writer = PdfWriter()
        for pdf_path in pdf_paths:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def split_pdf(pdf_path: str, start_page: int, end_page: int) -> bytes:
        """Split PDF pages"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
            writer.add_page(reader.pages[page_num])
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def protect_pdf(pdf_path: str, password: str) -> bytes:
        """Protect PDF with an open password."""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        if reader.is_encrypted:
            result = reader.decrypt(password)
            if result == 0:
                raise ValueError("PDF is already encrypted. Unlock it first or use the correct password.")

        for page in reader.pages:
            writer.add_page(page)

        # user_password makes the PDF ask for a password when opened.
        # owner_password keeps an owner key for permission management.
        writer.encrypt(user_password=password, owner_password=password)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output.getvalue()


    @staticmethod
    def restrict_permissions(pdf_path: str, can_print: bool = False,
                            can_edit: bool = False, can_copy: bool = False,
                            owner_password: str = "restricted") -> bytes:
        """Restrict PDF permissions while allowing the file to open without a password."""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        permissions = UserAccessPermissions(0)
        if can_print:
            permissions |= UserAccessPermissions.PRINT
        if can_edit:
            permissions |= UserAccessPermissions.MODIFY
        if can_copy:
            permissions |= UserAccessPermissions.EXTRACT

        writer.encrypt(
            user_password="",
            owner_password=owner_password or "restricted",
            permissions_flag=permissions,
        )

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def get_pdf_metadata(pdf_path: str) -> dict:
        """Get PDF metadata"""
        doc = fitz.open(pdf_path)
        return {
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
        }
