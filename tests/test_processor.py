from pathlib import Path

import pytest

from ..src.thai_ocr.processor import OCRConfig, OCRError, ThaiOCRProcessor


@pytest.fixture
def processor() -> ThaiOCRProcessor:
    return ThaiOCRProcessor()


def test_config_defaults() -> None:
    config = OCRConfig()

    assert config.language == "tha"
    assert config.psm_mode == 6
    assert ".pdf" in config.supported_formats
    assert ".png" in config.supported_formats


def test_unsupported_format(processor: ThaiOCRProcessor, tmp_path: Path) -> None:
    input_path: Path = tmp_path / "test.unsupported"
    output_path: Path = tmp_path / "output.txt"

    # Create dummy file
    input_path.write_text(data="")

    with pytest.raises(expected_exception=ValueError, match="Unsupported file format"):
        processor.process_document(input_path=input_path, output_path=output_path)


def test_process_image_with_invalid_path(processor: ThaiOCRProcessor) -> None:
    with pytest.raises(expected_exception=OCRError):
        processor.process_image(image="nonexistent.png")
