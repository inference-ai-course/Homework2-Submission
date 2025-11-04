"""
Whisper Transcription Bot for YouTube Conference Talks
Downloads audio from YouTube videos and transcribes using Whisper AI
Performs OCR on video frames for text extraction
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import os, shutil


# ----- FFmpeg bootstrap (for Whisper) -----
FFMPEG_BIN = "C:\\ffmpeg\\bin"       # change if you installed elsewhere
ffmpeg_exe  = os.path.join(FFMPEG_BIN, "ffmpeg.exe")
ffprobe_exe = os.path.join(FFMPEG_BIN, "ffprobe.exe")

# add to PATH for this Python process
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

# sanity print (should show full paths, not None)
print("ffmpeg:", shutil.which("ffmpeg"))
print("ffprobe:", shutil.which("ffprobe"))

if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")
else:
    print("✗ FFmpeg not found at", FFMPEG_BIN)
    print("  Expecting ffmpeg.exe and ffprobe.exe in that folder.")
    # you can exit here if you want:
    # raise FileNotFoundError("Install FFmpeg and set FFMPEG_BIN")
    
print("ffmpeg on PATH:", shutil.which("ffmpeg"))
print("ffprobe on PATH:", shutil.which("ffprobe"))
# ------------------------------------------
# Check for required dependencies
try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp not installed. Run: python -m pip install yt-dlp")
    exit(1)

try:
    import whisper
except ImportError:
    print("ERROR: openai-whisper not installed. Run: python -m pip install openai-whisper")
    exit(1)

try:
    import cv2
except ImportError:
    print("WARNING: opencv-python not installed. Frame extraction disabled.")
    print("Install with: python -m pip install opencv-python")
    cv2 = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("WARNING: pytesseract/pillow not installed. OCR disabled.")
    print("Install with: python -m pip install pytesseract pillow")
    pytesseract = None

try:
    import numpy as np
except ImportError:
    print("WARNING: numpy not installed.")
    print("Install with: python -m pip install numpy")
    np = None

# Configure Tesseract path (Windows)
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"✓ Tesseract configured at: {TESSERACT_PATH}\n")
else:
    print(f"⚠ WARNING: Tesseract not found at: {TESSERACT_PATH}")
    print("Please update TESSERACT_PATH in the script\n")


class WhisperTranscriptionBot:
    def __init__(self, output_dir="transcriptions", model_size="base"):
        """
        Initialize Whisper transcription bot
        
        Args:
            output_dir: Directory to save transcriptions and audio files
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: fastest, least accurate
                       - base: good balance (recommended for testing)
                       - small: better accuracy
                       - medium/large: best accuracy, slowest
        """
        self.output_dir = Path(output_dir)
        self.audio_dir = self.output_dir / "audio"
        self.transcript_dir = self.output_dir / "transcripts"
        self.frames_dir = self.output_dir / "frames"
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)
        self.transcript_dir.mkdir(exist_ok=True)
        self.frames_dir.mkdir(exist_ok=True)
        
        self.model_size = model_size
        self.model = None
        self.processed_videos = []
        
    def load_whisper_model(self):
        """Load Whisper model"""
        if self.model is None:
            print(f"→ Loading Whisper model: {self.model_size}")
            print("  (First time will download the model)")
            try:
                self.model = whisper.load_model(self.model_size)
                print(f"✓ Whisper model loaded: {self.model_size}\n")
            except Exception as e:
                print(f"✗ Error loading Whisper model: {str(e)}")
                raise
    
    def download_audio(self, youtube_url, video_id=None):
        """
        Download audio from YouTube video
        
        Args:
            youtube_url: YouTube video URL
            video_id: Optional custom video ID (otherwise extracted from URL)
        Returns:
            Path to downloaded audio file
        """
        try:
            # Extract video ID from URL if not provided
            if not video_id:
                if "v=" in youtube_url:
                    video_id = youtube_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in youtube_url:
                    video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                else:
                    video_id = f"video_{int(time.time())}"
            
            audio_path = self.audio_dir / f"{video_id}.mp3"
            
            # Skip if already downloaded
            if audio_path.exists():
                print(f"  → Audio already exists: {audio_path.name}")
                return audio_path, None, None
            
            print(f"  → Downloading audio from YouTube...")
            
            # Set FFmpeg location - UPDATE THIS PATH IF NEEDED
            ffmpeg_location = "C:\\ffmpeg\\bin"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.audio_dir / f"{video_id}.%(ext)s"),
                'ffmpeg_location': ffmpeg_location,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                print(f"  ✓ Downloaded: {title}")
                print(f"  ✓ Duration: {duration//60}:{duration%60:02d}")
                print(f"  ✓ Saved to: {audio_path.name}")
                
                return audio_path, title, duration
                
        except Exception as e:
            print(f"  ✗ Error downloading audio: {str(e)}")
            return None, None, None
    
    def transcribe_audio(self, audio_path, language="en"):
        """
        Transcribe audio using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en' for English)
        Returns:
            Transcription result with timestamps
        """
        try:
            print(f"  → Transcribing with Whisper ({self.model_size} model)...")
            print(f"  → This may take a few minutes...")
            
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            print(f"  ✓ Transcription complete!")
            return result
            
        except Exception as e:
            print(f"  ✗ Error transcribing audio: {str(e)}")
            return None
    
    def extract_video_frames(self, youtube_url, video_id, num_frames=10):
        """
        Extract frames from YouTube video for OCR
        
        Args:
            youtube_url: YouTube video URL
            video_id: Video ID for naming
            num_frames: Number of frames to extract
        Returns:
            List of frame paths
        """
        if cv2 is None:
            print("  ⚠ OpenCV not available. Skipping frame extraction.")
            return []
            
        try:
            print(f"  → Extracting {num_frames} frames for OCR...")
            
            # Download video (low quality for faster processing)
            video_path = self.frames_dir / f"{video_id}_temp.mp4"
            
            # Set FFmpeg location
            ffmpeg_location = "C:\\ffmpeg\\bin"
            
            ydl_opts = {
                'format': 'worst[ext=mp4]',  # Lowest quality for speed
                'outtmpl': str(video_path),
                'ffmpeg_location': ffmpeg_location,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Extract frames
            cap = cv2.VideoCapture(str(video_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // num_frames)
            
            frame_paths = []
            frame_count = 0
            
            for i in range(0, total_frames, frame_interval):
                if frame_count >= num_frames:
                    break
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret:
                    frame_path = self.frames_dir / f"{video_id}_frame_{frame_count:03d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(frame_path)
                    frame_count += 1
            
            cap.release()
            
            # Clean up video file
            if video_path.exists():
                video_path.unlink()
            
            print(f"  ✓ Extracted {len(frame_paths)} frames")
            return frame_paths
            
        except Exception as e:
            print(f"  ✗ Error extracting frames: {str(e)}")
            return []
    
    def ocr_frames(self, frame_paths):
        """
        Perform OCR on video frames
        
        Args:
            frame_paths: List of frame image paths
        Returns:
            Combined OCR text from all frames
        """
        if pytesseract is None:
            print("  ⚠ Pytesseract not available. Skipping OCR.")
            return ""
            
        try:
            print(f"  → Performing OCR on {len(frame_paths)} frames...")
            
            all_text = []
            
            for i, frame_path in enumerate(frame_paths):
                try:
                    from PIL import Image
                    img = Image.open(frame_path)
                    text = pytesseract.image_to_string(img)
                    
                    if text.strip():
                        all_text.append(f"\n--- Frame {i+1} ---\n{text.strip()}")
                except Exception as e:
                    print(f"    ✗ Error on frame {i+1}: {str(e)}")
                    continue
            
            combined_text = "\n".join(all_text)
            print(f"  ✓ OCR complete on {len(frame_paths)} frames")
            
            return combined_text
            
        except Exception as e:
            print(f"  ✗ Error performing OCR: {str(e)}")
            return ""
    
    def format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def save_transcript(self, video_id, title, transcript_result, ocr_text="", youtube_url=""):
        """
        Save transcript to JSON file with timestamps
        
        Args:
            video_id: Video ID
            title: Video title
            transcript_result: Whisper transcription result
            ocr_text: OCR text from video frames
            youtube_url: Original YouTube URL
        """
        try:
            transcript_path = self.transcript_dir / f"{video_id}.json"
            
            # Format segments with timestamps
            segments = []
            for segment in transcript_result.get('segments', []):
                segments.append({
                    'start': self.format_timestamp(segment['start']),
                    'end': self.format_timestamp(segment['end']),
                    'start_seconds': segment['start'],
                    'end_seconds': segment['end'],
                    'text': segment['text'].strip()
                })
            
            # Create transcript object
            transcript_data = {
                'video_id': video_id,
                'title': title,
                'url': youtube_url,
                'transcribed_at': datetime.now().isoformat(),
                'model': self.model_size,
                'language': transcript_result.get('language', 'unknown'),
                'full_text': transcript_result.get('text', ''),
                'segments': segments,
                'ocr_text': ocr_text
            }
            
            # Save to JSON
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Saved transcript to: {transcript_path.name}")
            
            # Also save a readable text version
            txt_path = self.transcript_dir / f"{video_id}.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"YouTube Video Transcript\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"Title: {title}\n")
                f.write(f"URL: {youtube_url}\n")
                f.write(f"Video ID: {video_id}\n")
                f.write(f"Transcribed: {datetime.now().isoformat()}\n")
                f.write(f"Model: Whisper {self.model_size}\n\n")
                f.write(f"{'='*60}\n")
                f.write(f"FULL TRANSCRIPT\n")
                f.write(f"{'='*60}\n\n")
                f.write(transcript_result.get('text', ''))
                f.write(f"\n\n{'='*60}\n")
                f.write(f"TIMESTAMPED SEGMENTS\n")
                f.write(f"{'='*60}\n\n")
                
                for seg in segments:
                    f.write(f"[{seg['start']} --> {seg['end']}]\n")
                    f.write(f"{seg['text']}\n\n")
                
                if ocr_text:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"OCR TEXT FROM VIDEO FRAMES\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(ocr_text)
            
            print(f"  ✓ Saved readable transcript to: {txt_path.name}")
            
            return transcript_data
            
        except Exception as e:
            print(f"  ✗ Error saving transcript: {str(e)}")
            return None
    
    def process_video(self, youtube_url, extract_frames=True):
        """
        Process a single YouTube video: download audio, transcribe, and OCR
        
        Args:
            youtube_url: YouTube video URL
            extract_frames: Whether to extract frames for OCR
        Returns:
            Transcript data
        """
        print(f"\n{'='*60}")
        print(f"Processing: {youtube_url}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Download audio
            result = self.download_audio(youtube_url)
            if result[0] is None:
                return None
            
            audio_path, title, duration = result
            # Extract or fallback video_id
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = f"video_{int(time.time())}"

            # If title wasn't returned (when file already existed), set a placeholder
            if not title:
                title = f"Video {video_id}"
            # Extract video ID
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = f"video_{int(time.time())}"
            
            # Step 2: Load Whisper model
            self.load_whisper_model()
            
            # Step 3: Transcribe audio
            transcript_result = self.transcribe_audio(audio_path)
            if not transcript_result:
                return None
            
            # Step 4: Extract frames and perform OCR (optional)
            ocr_text = ""
            if extract_frames:
                frame_paths = self.extract_video_frames(youtube_url, video_id, num_frames=10)
                if frame_paths:
                    ocr_text = self.ocr_frames(frame_paths)
            
            # Step 5: Save transcript
            transcript_data = self.save_transcript(
                video_id, 
                title, 
                transcript_result, 
                ocr_text,
                youtube_url
            )
            
            if transcript_data:
                self.processed_videos.append(transcript_data)
                print(f"\n✓ Successfully processed: {title}")
            
            return transcript_data
            
        except Exception as e:
            print(f"\n✗ Error processing video: {str(e)}")
            return None
    
    def process_multiple_videos(self, youtube_urls, extract_frames=True):
        """
        Process multiple YouTube videos
        
        Args:
            youtube_urls: List of YouTube URLs
            extract_frames: Whether to extract frames for OCR
        """
        total = len(youtube_urls)
        print(f"\n{'='*60}")
        print(f"Batch Processing: {total} videos")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        for i, url in enumerate(youtube_urls, 1):
            print(f"\n[{i}/{total}] ", end='')
            self.process_video(url, extract_frames)
            
            # Small delay between videos
            if i < total:
                time.sleep(2)
        
        # Summary
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Successfully processed: {len(self.processed_videos)}/{total} videos")
        print(f"Total time: {elapsed/60:.1f} minutes")
        print(f"Output location: {self.transcript_dir}")
        print(f"{'='*60}")
    
    def create_summary(self):
        """Create a summary JSON of all transcriptions"""
        summary_path = self.output_dir / "talks_transcripts.json"
        
        summary_data = {
            'generated_at': datetime.now().isoformat(),
            'total_videos': len(self.processed_videos),
            'model': self.model_size,
            'videos': self.processed_videos
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Summary saved to: {summary_path}")
        return summary_path


def main():
    """
    Example usage for transcribing conference talks
    """
    print("="*60)
    print("Whisper Transcription Bot for YouTube Conference Talks")
    print("Task 3: Automatic Speech Recognition")
    print("="*60)
    print()
    
    # Example YouTube URLs (3-minute NLP conference talks)
    # YouTube URLs for NLP conference talks and tutorials (~3 minutes)
    youtube_urls = [
        # 1. BERT Introduction (3 min)
        "https://www.youtube.com/watch?v=ioGry-89gqE",  # Language Processing with BERT: The 3 Minute Intro
        
        # 2. Sentiment Analysis (4 min)
        "https://www.youtube.com/watch?v=AJVP96tAWxw",  # Sentiment Analysis in 4 Minutes
        
        # 3. ACL 2024 Best Paper
        "https://www.youtube.com/watch?v=BYq9n3lFJRc",  # Mission: Impossible Language Models | ACL 2024
        
        # 4. NLP in 60 seconds
        "https://www.youtube.com/watch?v=43cXcuXGnXk",  # What Is Natural Language Processing (NLP)? 60 Seconds
        
        # 5. EMNLP 2023 Workshop
        "https://www.youtube.com/watch?v=Rq6LG2D2Nco",  # PyTAIL Presentation | NLP-OSS 2023 | EMNLP 2023
        
        # 6. ACL 2021 Outstanding Paper
        "https://www.youtube.com/watch?v=oAM0Sr1WNW0",  # UnNatural Language Inference (ACL 2021 Outstanding Paper)
        
        # 7. NAACL 2022
        "https://www.youtube.com/watch?v=JLrvzZAMs2Y",  # Named Entity Recognition as Multi-Question MRC - NAACL 2022
        
        # 8. EMNLP 2023 Best Theme Paper
        "https://www.youtube.com/watch?v=cmge3fFfZMc",  # HackAPrompt Best Theme Paper at EMNLP 2023
        
        # 9. NAACL 2024
        "https://www.youtube.com/watch?v=7ofrbSPT1fA",  # PEEB: Part-based Image Classifiers - NAACL 2024
        
        # 10. A Short Intro to Efficient NLP
        "https://www.youtube.com/watch?v=2LcZjPPJfWo",  # A Short Introduction to Efficient NLP
    ]
    
    # Initialize bot
    bot = WhisperTranscriptionBot(
        output_dir="transcriptions",
        model_size="base"  # Options: tiny, base, small, medium, large
    )
    
    # Process videos
    # Set extract_frames=False if you don't need OCR from video frames
    bot.process_multiple_videos(
        youtube_urls,
        extract_frames=True  # Set to True to include OCR from video frames
    )
    
    # Create summary
    bot.create_summary()
    
    print("\n" + "="*60)
    print("✓ Transcription completed!")
    print(f"✓ Check the 'transcriptions/transcripts/' folder")
    print("="*60)


if __name__ == "__main__":
    main()