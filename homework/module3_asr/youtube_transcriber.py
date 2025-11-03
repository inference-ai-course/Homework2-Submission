#!/usr/bin/env python3
"""
youtube_transcriber.py
Module 3: Automatic Speech Recognition (ASR)
Transcribes YouTube videos using Whisper.
Christine Zhao
2025-11-02
"""

import os
import json
import subprocess
import whisper
from typing import List, Dict


class YouTubeTranscriber:
    """Transcribes YouTube videos using yt-dlp and Whisper."""

    def __init__(self, output_file: str = "talks_transcripts.jsonl"):
        """
        Initialize the transcriber.

        Args:
            output_file: Output JSONL file for transcripts
        """
        self.output_file = output_file
        self.model = None

    def load_whisper_model(self, model_size: str = "base"):
        """
        Load Whisper model.

        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Model loaded successfully.")

    def download_audio(self, url: str, output_path: str) -> bool:
        """
        Download audio from YouTube using yt-dlp.

        Args:
            url: YouTube video URL
            output_path: Path to save the audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Downloading audio from: {url}")

            # Use yt-dlp to download audio only
            cmd = [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "-o", output_path,
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Audio downloaded: {output_path}")
                return True
            else:
                print(f"Error downloading audio: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error downloading audio: {e}")
            return False

    def transcribe_audio(self, audio_path: str, video_info: Dict) -> Dict:
        """
        Transcribe audio using Whisper.

        Args:
            audio_path: Path to audio file
            video_info: Dictionary with video metadata

        Returns:
            Dictionary with transcription results
        """
        try:
            print(f"Transcribing: {audio_path}")

            if not self.model:
                self.load_whisper_model()

            # Transcribe with Whisper
            result = self.model.transcribe(audio_path, verbose=True)

            # Build transcript with timestamps
            transcript_data = {
                "url": video_info.get("url", ""),
                "title": video_info.get("title", ""),
                "duration": video_info.get("duration", ""),
                "full_text": result["text"],
                "segments": []
            }

            # Add segments with timestamps
            for segment in result["segments"]:
                transcript_data["segments"].append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })

            return transcript_data

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def process_videos(self, video_list: List[Dict]):
        """
        Process a list of videos and transcribe them.

        Args:
            video_list: List of dictionaries with video URLs and metadata
        """
        if not self.model:
            self.load_whisper_model()

        transcripts = []

        for i, video_info in enumerate(video_list, 1):
            url = video_info.get("url", "")
            title = video_info.get("title", f"Video {i}")

            print(f"\n{'='*60}")
            print(f"Processing video {i}/{len(video_list)}: {title}")
            print(f"URL: {url}")
            print('='*60)

            # Download audio
            audio_filename = f"audio_{i}.mp3"
            if not self.download_audio(url, audio_filename):
                print(f"Skipping video {i} due to download error.")
                continue

            # Transcribe
            transcript = self.transcribe_audio(audio_filename, video_info)

            if transcript:
                transcripts.append(transcript)

            # Clean up audio file
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

        # Save to JSONL
        self.save_transcripts(transcripts)

    def save_transcripts(self, transcripts: List[Dict]):
        """
        Save transcripts to JSONL file.

        Args:
            transcripts: List of transcript dictionaries
        """
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for transcript in transcripts:
                f.write(json.dumps(transcript, ensure_ascii=False) + '\n')

        print(f"\n{'='*60}")
        print(f"Transcripts saved to: {self.output_file}")
        print(f"Total videos transcribed: {len(transcripts)}")
        print('='*60)


def main():
    """Main function to run transcription."""

    # Example video list - Replace with actual NLP conference talks
    video_list = [
        {
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "title": "Neural Networks Explained",
            "duration": "180"
        },
        {
            "url": "https://www.youtube.com/watch?v=IHZwWFHWa-w",
            "title": "Transformers Architecture",
            "duration": "180"
        },
        # Add more videos as needed (up to 10 short talks)
    ]

    transcriber = YouTubeTranscriber()
    transcriber.process_videos(video_list)


if __name__ == "__main__":
    main()
