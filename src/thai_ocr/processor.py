from __future__ import annotations

import logging
import shutil
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


@dataclass
class OCRConfig:
    """Configuration for OCR processing.

    Note:
        - Tesseract must be installed and accessible in system PATH or provided via tesseract_path
        - For PDF processing, Poppler must be installed and accessible in system PATH or provided via poppler_path
    """  # noqa: E501, E501

    tesseract_path: str | None = None
    poppler_path: str | None = None
    language: str = "tha"
    psm_mode: int = 6  # assume uniform black of text
    supported_formats: set[str] = field(
        default_factory=lambda: {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    )

    def __post_init__(self) -> None:
        # Check for Poppler
        if not self.poppler_path and not shutil.which("pdftoppm"):
            self.poppler_path = r"C:\Program Files\poppler\Library\bin"

        # Check for Tesseract
        if not self.tesseract_path:
            if shutil.which("tesseract"):
                self.tesseract_path = shutil.which("tesseract")
            else:
                # Common Windows installation path
                default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                if Path(default_path).exists():
                    self.tesseract_path = default_path


class OCRError(Exception):
    """Base exception for OCR processing errors."""


class ThaiOCRProcessor:
    """Process documents for Thai text extraction using OCR."""

    def __init__(self, config: OCRConfig | None = None) -> None:
        """Initialize the Thai OCR processor.

        Args:
            config: Optional configuration for OCR processing.

        Raises:
            OCRError: If Tesseract is not properly configured.
        """
        self.config: OCRConfig = config or OCRConfig()
        self._setup_logging()

        # Validate Tesseract installation
        if self.config.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path

        try:
            pytesseract.get_tesseract_version()
        except Exception as error:
            message = (
                "Tesseract is required but not properly configured. Please:\n"
                "1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Add it to system PATH or provide path via OCRConfig(tesseract_path=...)"  # noqa: E501
            )
            self.logger.error(msg=message)
            raise OCRError(message) from error

    def _setup_logging(self) -> None:
        """Configure logging for the processor."""

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger: logging.Logger = logging.getLogger(name=__name__)

    def convert_pdf_to_images(self, pdf_path: str | Path) -> Sequence[Image.Image]:
        """Convert PDF pages to images.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Sequence of PIL Image objects.

        Raises:
            OCRError: If PDF conversion fails due to missing Poppler or other errors.
        """

        try:
            return convert_from_path(
                pdf_path=str(pdf_path), poppler_path=self.config.poppler_path
            )
        except Exception as error:
            if "poppler" in str(error).lower():
                message = (
                    "Poppler is required for PDF processing. Please install Poppler and ensure "  # noqa: E501
                    "it's in your system PATH, or provide its path via OCRConfig(poppler_path=...).\n"  # noqa: E501
                    "Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases"
                )
            else:
                message = f"Error converting PDF to images: {error}"
            self.logger.error(msg=message)
            raise OCRError(message) from error

    def process_image(self, image: str | Path | Image.Image) -> str:
        """
        Process a single image and extract Thai text.

        Args:
            image: Image path or PIL Image object

        Returns:
            Extracted text

        Raises:
            OCRError: If image processing fails.
        """

        try:
            # Load image if path is provided
            if isinstance(image, str | Path):
                image = Image.open(fp=image)

            # Extract text with Thai language configuration
            text: Any = pytesseract.image_to_string(
                image=image,
                lang=self.config.language,
                config=f"--psm {self.config.psm_mode}",
            )
            return text.strip()
        except Exception as error:
            if "tesseract is not installed" in str(error):
                message = (
                    "Tesseract is not properly configured. Please:\n"
                    "1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "2. Add it to system PATH or provide path via OCRConfig(tesseract_path=...)"  # noqa: E501
                )
            else:
                message = f"Error processing image: {error}"
            self.logger.error(msg=message)
            raise OCRError(message) from error

    def process_document(self, input_path: str | Path, output_path: str | Path) -> None:
        """Process document and save extracted text.

        Args:
            input_path: Path to input document.
            output_path: Path to save extracted text.

        Raises:
            OCRError: If document processing fails.
            ValueError: If file format is not supported.
        """

        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            self.logger.info(msg=f"Processing document: {input_path}")
            file_ext: str = input_path.suffix.lower()

            if file_ext not in self.config.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")

            extracted_text: list[str] = []

            # Handle PDF files
            if file_ext == ".pdf":
                images: Sequence[Image.Image] = self.convert_pdf_to_images(
                    pdf_path=input_path
                )
                for i, image in enumerate(iterable=images, start=1):
                    self.logger.info(msg=f"Processing page {i}")
                    page_text: str = self.process_image(image=image)
                    extracted_text.append(f"=== Page {i} ===\n{page_text}\n")

            # Handle image files
            else:
                text: str = self.process_image(image=input_path)
                extracted_text.append(text)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save extracted text
            output_path.write_text(data="\n".join(extracted_text), encoding="utf-8")
            self.logger.info(msg=f"Text saved to: {output_path}")

        except Exception as error:
            message: str = f"Error processing document: {error}"
            self.logger.error(msg=message)
            raise OCRError(message) from error
