# Thai OCR Processor

A Python application for extracting Thai text from PDF documents and images using Tesseract OCR. Supports both command-line and graphical user interfaces.

## Features

- Extract Thai text from PDF documents and images (PNG, JPG, TIFF, BMP)
- Support for multi-page PDF documents
- Easy-to-use graphical interface
- Command-line interface for batch processing
- Progress tracking and error handling
- Text saving in UTF-8 format

## Requirements

- Python 3.12 or higher
- Tesseract OCR with Thai language support
- Poppler (for PDF processing)

### Installing Dependencies

1. Install Tesseract OCR:

   - Windows: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-thai`
   - macOS: `brew install tesseract tesseract-lang`

2. Install Poppler:

   - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
   - Linux: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

## Installation

1. Clone the repository:

```bash

git clone https://github.com/nanonymoussu/python_thai_ocr.git

cd thai-ocr

```

2. Create and activate a virtual environment (optional but recommended):

```bash

uv venv

source venv/bin/activate  # Linux/macOS

./venv/Scripts/activate   # Windows

```

3. Install the package and its dependencies:

```bash

pip install -e .

```

## Usage

### Graphical Interface

Run the GUI application:

```bash

python run_gui.py

```

### Command Line Interface

Process a single document:

```bash

python main.py input.pdf output.txt

```

Optional arguments:

```bash

python main.py --tesseract-path "C:\Program Files\Tesseract-OCR\tesseract.exe" input.pdf output.txt

```

## Configuration

The application will attempt to locate Tesseract and Poppler automatically. If they're not in the system PATH, you can specify their locations:

- Through the code:

```python

config = OCRConfig(

    tesseract_path="path/to/tesseract",

    poppler_path="path/to/poppler"

)

```

## Development

1. Install development dependencies:

```bash

pip install -e ".[dev]"

```

2. Run tests:

```bash

pytest

```

3. Check code quality:

```bash

black .

ruff check.

mypy .

```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
