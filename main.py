import argparse
import logging

from src.thai_ocr.processor import OCRConfig, ThaiOCRProcessor


def main() -> None:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Thai OCR Document Processor")
    parser.add_argument("input", help="Path to input documnet (PDF or image)")
    parser.add_argument("output", help="Path to output text file")
    parser.add_argument("--tesseract-path", help="Path to tesseract executable")
    args: argparse.Namespace = parser.parse_args()

    try:
        config = OCRConfig(tesseract_path=args.tesseract_path)
        processor = ThaiOCRProcessor(config=config)
        processor.process_document(input_path=args.input, output_path=args.output)
    except Exception as error:
        logging.error(msg=f"Processing failed: {error}")
        exit(code=1)


if __name__ == "__main__":
    main()
