"""
ocr_batch_processor.py

Brief description:
    Batch processes images in a specified input directory using Optical Character Recognition (OCR)
    to extract text content, and saves the results as plain text files.

Detailed description:
    - Scans a configured input folder for supported image formats.
    - Preprocesses each image (grayscale conversion, contrast adjustment, denoising)
      to improve OCR accuracy.
    - Uses Tesseract OCR to extract text from each image.
    - Saves extracted text to a corresponding .txt file in the output directory.
    - Supports concurrent processing of multiple images using a thread pool.

Usage:
    python ocr_batch_processor.py

Environment variables (optional):
    RAW_INPUT_FOLDER       - Base folder for raw input data (default: "01_ingest")
    PROCESSED_TASKS_FOLDER - Folder for processed tasks (default: "02_processed_tasks")
    CLEAN_CORPUS_FOLDER    - Folder for cleaned corpus output (default: "03_clean_corpus")
    OCR_IMAGE_FOLDER       - Subfolder containing images (default: "images")
    OCR_RESULT_FOLDER      - Subfolder for OCR text output (default: "ocr_output")
    OCR_LANGUAGE           - Tesseract OCR language code (default: "eng")
    OCR_PSM_MODE           - Tesseract page segmentation mode (default: 3)
    MAX_WORKER_THREADS     - Max concurrent threads (default: CPU count)
    OCR_ALPHA              - Alpha value for contrast adjustment (default: 1.5)
    OCR_BETA               - Beta value for brightness adjustment (default: 20)
    OCR_DENOISE_H          - Denoising strength (default: 30)

Dependencies:
    - OpenCV (cv2)
    - pytesseract
    - python-dotenv
"""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import cv2
import pytesseract
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Resolve base directory for relative paths
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration from environment variables
RAW_INPUT_FOLDER = os.getenv("RAW_INPUT_FOLDER", "01_ingest")
PROCESSED_TASKS_FOLDER = os.getenv("PROCESSED_TASKS_FOLDER", "02_processed_tasks")
CLEAN_CORPUS_FOLDER = os.getenv("CLEAN_CORPUS_FOLDER", "03_clean_corpus")

OCR_IMAGE_FOLDER = os.getenv("OCR_IMAGE_FOLDER", "images")
OCR_RESULT_FOLDER = os.getenv("OCR_RESULT_FOLDER", "ocr_output")

OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
OCR_PSM_MODE = int(os.getenv("OCR_PSM_MODE", "3"))
MAX_WORKER_THREADS = int(os.getenv("MAX_WORKER_THREADS", str(os.cpu_count())))

OCR_ALPHA = float(os.getenv("OCR_ALPHA", "1.5"))
OCR_BETA = int(os.getenv("OCR_BETA", "20"))
OCR_DENOISE_H = int(os.getenv("OCR_DENOISE_H", "30"))

SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tiff")

# Construct input and output paths
RAW_INPUT_PATH = Path(BASE_DIR) / RAW_INPUT_FOLDER / OCR_IMAGE_FOLDER
OUTPUT_TEXT_PATH = Path(BASE_DIR) / CLEAN_CORPUS_FOLDER / OCR_RESULT_FOLDER


class OCRBatchProcessor:
    """
    Batch OCR processor for extracting text from images.

    Responsibilities:
        - Locate supported image files in the input directory.
        - Preprocess images to enhance OCR accuracy.
        - Extract text using Tesseract OCR.
        - Save extracted text to output files.
        - Process multiple images concurrently.

    Attributes:
        input_dir (Path): Path to the directory containing input images.
        output_dir (Path): Path to the directory where OCR results will be saved.
    """

    def __init__(self):
        """
        Initialize the OCRBatchProcessor.

        Ensures that the input and output directories exist, creating them if necessary.
        """
        self.input_dir = RAW_INPUT_PATH
        self.output_dir = OUTPUT_TEXT_PATH
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Input directory: {self.input_dir}")
        logging.info(f"Output directory: {self.output_dir}")

    def preprocess_image(self, image_path: Path) -> Any:
        """
        Preprocess an image to improve OCR accuracy.

        Steps:
            1. Read the image from disk.
            2. Convert to grayscale.
            3. Adjust contrast and brightness.
            4. Apply denoising.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            Any: The preprocessed image array.

        Raises:
            ValueError: If the image cannot be read.
        """
        logging.debug(f"Reading image: {image_path}")
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        adjusted = cv2.convertScaleAbs(grayscale, alpha=OCR_ALPHA, beta=OCR_BETA)
        return cv2.fastNlMeansDenoising(adjusted, h=OCR_DENOISE_H)

    def extract_text(self, image: Any) -> str:
        """
        Extract text from a preprocessed image using Tesseract OCR.

        Args:
            image (Any): The preprocessed image array.

        Returns:
            str: The extracted text.
        """
        return pytesseract.image_to_string(
            image, lang=OCR_LANGUAGE, config=f"--psm {OCR_PSM_MODE}"
        )

    def process_image(self, file_path: Path) -> None:
        """
        Process a single image file:
            - Preprocess the image.
            - Extract text.
            - Save text to a .txt file.

        Args:
            file_path (Path): Path to the image file.
        """
        logging.info(f"Processing: {file_path.name}")
        output_file = self.output_dir / f"{file_path.stem}.txt"
        try:
            processed = self.preprocess_image(file_path)
            text = self.extract_text(processed)
            output_file.write_text(text.strip(), encoding="utf-8")
            if text.strip():
                logging.info(f"Text saved: {output_file.name}")
            else:
                logging.warning(f"No text found in: {file_path.name}")
        except Exception as e:
            logging.error(f"Failed to process {file_path.name}: {e}")

    def run(self, max_workers: int = MAX_WORKER_THREADS):
        """
        Run the batch OCR process.

        Steps:
            1. Identify all supported image files in the input directory.
            2. Process images concurrently using a thread pool.
            3. Log the number of successes and failures.

        Args:
            max_workers (int): Maximum number of worker threads to use.
        """
        files = [
            f
            for f in self.input_dir.iterdir()
            if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ]
        logging.info(f"Found {len(files)} image(s) to process.")
        if not files:
            logging.warning("No images found.")
            return
        success, failure = 0, 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_image, f): f for f in files}
            for future in as_completed(futures):
                try:
                    future.result()
                    success += 1
                except Exception:
                    failure += 1
        logging.info(f"OCR complete: {success} succeeded, {failure} failed.")


def main():
    """
    Main entry point for the OCR batch processor script.

    Initializes the processor and runs the OCR workflow.
    Exits with a non-zero status code if an unhandled exception occurs.
    """
    logging.info("OCR batch script started.")
    try:
        processor = OCRBatchProcessor()
        processor.run()
        logging.info("OCR batch script finished successfully.")
    except Exception as e:
        logging.exception(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
