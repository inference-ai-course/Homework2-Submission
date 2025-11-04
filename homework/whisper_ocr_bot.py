"""
whisper_ocr_bot.py

A batch-processing tool for automating the transcription and OCR extraction of
YouTube videos. This script reads a curated list of talks or presentations from
a text file, downloads each video, transcribes its audio using OpenAI's Whisper
speech-to-text model, and extracts on-screen text at fixed intervals using
Tesseract OCR.

**Input File Format**
The input file must contain alternating lines of:
    1. A descriptive title for the talk
    2. The corresponding YouTube URL

Example:
    1. Inspiring Talk on Leadership
       https://www.youtube.com/watch?v=example123
    2. AI in Healthcare
       https://www.youtube.com/watch?v=example456

**Configuration**
Settings are loaded from a `.env` file or environment variables:
    - YOUTUBE_LINKS_FOLDER: Folder containing the links file
    - YOUTUBE_LINKS_FILENAME: Name of the links file
    - OUTPUT_FILE: Name of the output JSONL file
    - FRAME_INTERVAL_SEC: Seconds between OCR frame captures
    - WHISPER_MODEL: Whisper model size (e.g., base, small, medium, large)
    - OCR_LANGUAGE: Language code for Tesseract OCR
    - OCR_PSM_MODE: Page segmentation mode for Tesseract
    - LOG_LEVEL: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

**Output**
A JSON Lines (.jsonl) file in the `02_processed_tasks` directory, where each line
is a JSON object containing:
    - title: Talk title
    - url: YouTube URL
    - downloaded_at: UTC timestamp of processing
    - segments: Whisper transcription segments
    - ocr_texts: OCR results with timestamps

**Usage**
    python whisper_ocr_bot.py
"""

import json
import logging
import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import cv2
import pytesseract
import whisper
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

YOUTUBE_LINKS_FOLDER = Path(os.getenv("YOUTUBE_LINKS_FOLDER", "01_ingest"))
YOUTUBE_LINKS_FILENAME = os.getenv("YOUTUBE_LINKS_FILENAME", "youtube_links.txt")
OUTPUT_DIR = Path("02_processed_tasks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / os.getenv("OUTPUT_FILE", "talks_transcripts.jsonl")
FRAME_INTERVAL_SEC = int(os.getenv("FRAME_INTERVAL_SEC", "10"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
OCR_PSM_MODE = os.getenv("OCR_PSM_MODE", "3")


class WhisperOCRBot:
    """
    Automates the end-to-end process of downloading YouTube videos,
    transcribing their audio with Whisper, and extracting on-screen
    text using Tesseract OCR.

    Attributes:
        entries (list[dict]): List of dictionaries with 'title' and 'url' keys.
        output_file (Path): Path to the JSONL output file.
        frame_interval_sec (int): Interval in seconds between OCR frame captures.
        ocr_language (str): Language code for OCR processing.
        ocr_psm_mode (str): Page segmentation mode for OCR.
        whisper_model_name (str): Name of the Whisper model to load.
        model: Loaded Whisper model instance.
    """

    def __init__(self):
        """
        Initialize the bot by:
            - Reading the links file from the configured folder
            - Parsing it into title/URL pairs
            - Loading the Whisper model into memory

        Raises:
            FileNotFoundError: If the links file does not exist.
        """
        links_file = YOUTUBE_LINKS_FOLDER / YOUTUBE_LINKS_FILENAME
        if not links_file.exists():
            logging.error(f"Links file not found: {links_file}")
            raise FileNotFoundError(f"No such file: {links_file}")
        self.entries = []
        with open(links_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            for i in range(0, len(lines), 2):
                title = lines[i]
                url = lines[i + 1] if i + 1 < len(lines) else None
                if url:
                    self.entries.append({"title": title, "url": url})
        if not self.entries:
            logging.warning("No valid title/URL pairs found in links file.")
        self.output_file = OUTPUT_FILE
        self.frame_interval_sec = FRAME_INTERVAL_SEC
        self.ocr_language = OCR_LANGUAGE
        self.ocr_psm_mode = OCR_PSM_MODE
        self.whisper_model_name = WHISPER_MODEL
        logging.info(f"Loading Whisper model: {self.whisper_model_name}")
        self.model = whisper.load_model(self.whisper_model_name)

    def download_video_temp(self, url):
        """
        Download a YouTube video to a uniquely named temporary file.

        Args:
            url (str): The YouTube video URL.

        Returns:
            str: Path to the downloaded MP4 file.

        Raises:
            subprocess.CalledProcessError: If yt-dlp fails to download the video.
        """
        tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp4")
        logging.info(f"Downloading video: {url}")
        subprocess.run(["yt-dlp", "-f", "mp4", url, "-o", tmp_path], check=True)
        return tmp_path

    def transcribe(self, video_path):
        """
        Transcribe the audio from a video file using the loaded Whisper model.

        Args:
            video_path (str): Path to the video file.

        Returns:
            dict: Whisper transcription result containing segments and metadata.
        """
        logging.info(f"Transcribing: {video_path}")
        return self.model.transcribe(video_path)

    def extract_ocr(self, video_path):
        """
        Extract on-screen text from a video at fixed frame intervals.

        Args:
            video_path (str): Path to the video file.

        Returns:
            list[dict]: List of OCR results, each with:
                - timestamp (float): Time in seconds from start of video
                - text (str): Extracted text content
        """
        logging.info(f"Extracting OCR from: {video_path}")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            logging.warning(f"Unable to determine FPS for {video_path}")
            return []
        frame_interval = int(fps * self.frame_interval_sec)
        ocr_results = []
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                text = pytesseract.image_to_string(
                    frame, lang=self.ocr_language, config=f"--psm {self.ocr_psm_mode}"
                )
                if text.strip():
                    ocr_results.append(
                        {"timestamp": frame_idx / fps, "text": text.strip()}
                    )
            frame_idx += 1
        cap.release()
        return ocr_results

    def process_talk(self, title, url):
        """
        Process a single talk by:
            - Downloading the video
            - Transcribing its audio
            - Extracting OCR text
            - Packaging results into a structured dictionary

        Args:
            title (str): The talk's title.
            url (str): The talk's YouTube URL.

        Returns:
            dict: Processed talk data with transcription and OCR results.
        """
        video_file = self.download_video_temp(url)
        try:
            transcript = self.transcribe(video_file)
            ocr_texts = self.extract_ocr(video_file)
            return {
                "title": title,
                "url": url,
                "downloaded_at": datetime.utcnow().isoformat(),
                "segments": transcript.get("segments", []),
                "ocr_texts": ocr_texts,
            }
        finally:
            try:
                os.remove(video_file)
            except OSError as e:
                logging.warning(f"Could not delete temp file {video_file}: {e}")

    def run(self):
        """
        Process all talks in the entries list and write results to the output file.

        Iterates through each title/URL pair, processes the talk, and writes
        the resulting dictionary as a JSON object to the output file (one per line).
        """
        if not self.entries:
            logging.error("No entries to process.")
            return
        logging.info(f"Processing {len(self.entries)} talks")
        with open(self.output_file, "w", encoding="utf-8") as f:
            for idx, entry in enumerate(self.entries, start=1):
                try:
                    logging.info(f"[{idx}/{len(self.entries)}] {entry['title']}")
                    result = self.process_talk(entry["title"], entry["url"])
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
                except Exception as e:
                    logging.error(f"[{idx}/{len(self.entries)}] Error: {e}")
        logging.info(f"Done. Output saved to {self.output_file}")


def main():
    """
    Entry point for running the WhisperOCRBot as a standalone script.

    This function:
        1. Instantiates the WhisperOCRBot class.
        2. Calls its `run` method to process all talks in the input file.
        3. Catches and logs any unhandled exceptions at the ERROR level.

    Intended usage:
        Run this script directly from the command line:
            python whisper_ocr_bot.py
    """
    try:
        bot = WhisperOCRBot()
        bot.run()
    except Exception as e:
        logging.error(f"Unhandled error: {e}")


if __name__ == "__main__":
    main()
