from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .processor import ThaiOCRProcessor


class OCRWorker(QThread):
    """Worker thread for OCR processing."""

    finished = pyqtSignal(str)  # signal to emit the processed text
    error = pyqtSignal(str)  # signal to emit error messages
    progress = pyqtSignal(int)  # signal to emit progress updates

    def __init__(self, file_path: str | Path) -> None:
        super().__init__()

        self.file_path: str | Path = file_path
        self.processor = ThaiOCRProcessor()

    def run(self) -> None:
        try:
            # Create a temporary file for output
            temp_output = Path("temp_output.txt")

            # Process the document
            self.processor.process_document(
                input_path=self.file_path, output_path=temp_output
            )

            # Read the processed text
            text: str = temp_output.read_text(encoding="utf-8")

            # Clean up
            temp_output.unlink()

            # Emit the result
            self.finished.emit(text)

        except Exception as error:
            self.error.emit(str(error))


class ThaiOCRApp(QMainWindow):
    """Main window for the Thai OCR application."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Thai OCR Application")
        self.setMinimumSize(800, 600)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create UI elements
        self.setup_ui(layout)

        # Initialize variables
        self.current_worker: OCRWorker | None = None

    def setup_ui(self, layout: QVBoxLayout) -> None:
        """Set up the user interface elements."""

        # File selection area
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_button = QPushButton("Select File")
        select_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_button)
        layout.addLayout(file_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Extracted text will appear here...")
        layout.addWidget(self.text_display)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.process_button = QPushButton("Process Document")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_document)
        button_layout.addWidget(self.process_button)

        self.save_button = QPushButton("Save Text")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_text)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def select_file(self) -> None:
        """Open file dialog for selecting input document."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select Document",
            directory="",
            filter="Documents (*.pdf *.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*.*)",
        )

        if file_path:
            self.file_label.setText(Path(file_path).name)
            self.process_button.setEnabled(True)
            self.current_file: str = file_path

    def process_document(self) -> None:
        """Start the OCR processing in a separate thread."""

        if not hasattr(self, "current_file"):
            return

        # Disable buttons during processing
        self.process_button.setEnabled(False)
        self.save_button.setEnabled(False)

        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Clear previous text
        self.text_display.clear()

        # Create and start worker thread
        self.current_worker = OCRWorker(file_path=self.current_file)
        self.current_worker.finished.connect(self.processing_finished)
        self.current_worker.error.connect(self.processing_error)
        self.current_worker.start()

    def processing_finished(self, text: str) -> None:
        """Handle completion of OCR processing."""

        # Update UI
        self.progress_bar.setVisible(False)
        self.text_display.setText(text)
        self.process_button.setEnabled(True)
        self.save_button.setEnabled(True)

        # Show success message
        QMessageBox.information(
            self,
            "Success",
            "Document processing completed successfully!",
        )

    def processing_error(self, error_message: str) -> None:
        """Handle OCR processing errors."""

        # Update UI
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)

        title = "Error"
        if "tesseract" in error_message.lower():
            title = "Missing Dependency - Tesseract"
        elif "poppler" in error_message.lower():
            title = "Missing Dependency - Poppler"

        # Show error message
        QMessageBox.critical(
            self,
            title,
            error_message,
        )

    def save_text(self) -> None:
        """Save the extracted text to a file."""

        if not self.text_display.toPlainText():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save Text",
            directory="",
            filter="Text Files (*.txt);;All Files (*.*)",
        )

        if file_path:
            try:
                Path(file_path).write_text(
                    self.text_display.toPlainText(), encoding="utf-8"
                )
                QMessageBox.information(self, "Success", "Text saved successfully!")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save file:\n{str(e)}",
                )


def main() -> None:
    """Launch the GUI application."""
    app = QApplication(sys.argv)

    # Set up application style
    app.setStyle("Fusion")

    # Create and show the main window
    window = ThaiOCRApp()
    window.show()

    # Start the event loop
    sys.exit(app.exec())
