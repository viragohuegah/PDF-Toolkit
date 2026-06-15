"""Ghostscript Service - PDF compression"""
import subprocess
import io
from pathlib import Path
import platform

class GhostscriptService:
    QUALITY_SETTINGS = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
    }

    @staticmethod
    def compress_pdf(input_path: str, output_path: str, quality: str = "ebook") -> bool:
        """
        Compress PDF using Ghostscript
        
        Quality options:
        - screen: lowest quality, smallest file
        - ebook: medium quality
        - printer: high quality
        - prepress: highest quality
        """
        quality_setting = GhostscriptService.QUALITY_SETTINGS.get(quality, "/ebook")
        
        # Determine OS and set appropriate command
        if platform.system() == "Windows":
            gs_cmd = "gswin64c"  # or gswin32c for 32-bit
        else:
            gs_cmd = "gs"
        
        cmd = [
            gs_cmd,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={quality_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dDetectDuplicateImages",
            "-r150x150",
            f"-sOutputFile={output_path}",
            str(input_path),
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ghostscript compression failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("Ghostscript not found. Please install Ghostscript.")
