import os
import subprocess
from pathlib import Path
import yt_dlp
import whisper
import pytesseract
import cv2
import jsonlines
from tqdm import tqdm
import re

# CONFIG

AUDIO_DIR = Path("transcripts/audio")
FRAMES_DIR = Path("transcripts/frames")
OUTPUT_JSONL = Path("transcripts/talks_transcripts.jsonl")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

# DOWNLOAD AUDIO

def download_audio(url: str):
    """Download audio from YouTube video using yt-dlp."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{AUDIO_DIR}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = AUDIO_DIR / f"{info['id']}.mp3"
        return str(audio_path), info['title']

# TRANSCRIBE AUDIO (Whisper)

def transcribe_audio(audio_path: str):
    """Run Whisper ASR on audio file."""
    model = whisper.load_model("small")  # options: tiny, base, small, medium, large
    result = model.transcribe(audio_path)
    return result["segments"]   # includes timestamps

# EXTRACT FRAMES (for OCR)

def extract_frames(video_url: str, interval=5):
    """Extract video frames every N seconds."""
    FRAMES_DIR.mkdir(exist_ok=True, parents=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", video_url,
        "-vf", f"fps=1/{interval}",
        f"{FRAMES_DIR}/frame_%04d.jpg"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# OCR USING TESSERACT

def ocr_frames():
    """Run OCR on all frames and store timestamps."""
    ocr_results = []
    for img_path in sorted(FRAMES_DIR.glob("frame_*.jpg")):
        img = cv2.imread(str(img_path))
        text = pytesseract.image_to_string(img)
        text = re.sub(r'\s+', ' ', text.strip())
        if text:
            # infer approximate timestamp from filename (frame_0005.jpg -> 5 * interval)
            frame_num = int(re.findall(r'\d+', img_path.stem)[0])
            timestamp = frame_num * 5  # assuming frame every 5s
            ocr_results.append({"time": timestamp, "ocr_text": text})
    return ocr_results

# ALIGN OCR TEXT TO ASR SEGMENTS

def align_ocr_to_transcripts(transcripts, ocr_data):
    """Attach OCR text that occurs near each transcript segment."""
    for seg in transcripts:
        seg_start, seg_end = seg["start"], seg["end"]
        seg["ocr_texts"] = [
            ocr["ocr_text"]
            for ocr in ocr_data
            if seg_start <= ocr["time"] <= seg_end
        ]
    return transcripts

# SAVE TO JSONL

def save_jsonl(title: str, transcripts):
    """Append talk transcripts to JSONL file."""
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(OUTPUT_JSONL, mode='a') as writer:
        writer.write({
            "title": title,
            "segments": transcripts
        })

# MAIN PROCESS

def process_talk(url):
    print(f"\n🎬 Processing: {url}")
    audio_path, title = download_audio(url)
    print(f"→ Downloaded: {title}")

    print("🗣️ Transcribing audio with Whisper...")
    transcripts = transcribe_audio(audio_path)

    print("🖼️ Extracting frames & running OCR...")
    extract_frames(url)
    ocr_data = ocr_frames()

    print("⏱️ Aligning OCR text with Whisper timestamps...")
    aligned_transcripts = align_ocr_to_transcripts(transcripts, ocr_data)

    print("💾 Saving results...")
    save_jsonl(title, aligned_transcripts)

    print(f"✅ Finished: {title}\n")

# RUN PIPELINE

if __name__ == "__main__":
    talk_urls = [
        # 10 NLP conference talk URLs
        "https://www.youtube.com/watch?v=2Ki7nRLuO_8",
        "https://www.youtube.com/shorts/aIJzsso7siE",
        "https://www.youtube.com/shorts/W8NxqDdYubQ",
        "https://www.youtube.com/shorts/_yqruiqyVm4",
        "https://www.youtube.com/shorts/8jkKTBfFN_U",
        "https://www.youtube.com/shorts/W8NxqDdYubQ",
        "https://www.youtube.com/shorts/jWfz8RA_9L0",
        "https://www.youtube.com/shorts/OGw5rzUtY3M",
        "https://www.youtube.com/shorts/brBz8Phzc4Y",
        "https://www.youtube.com/shorts/zdhK6IOGGCU"
    ]

    for url in tqdm(talk_urls, desc="Processing Talks"):
        try:
            process_talk(url)
        except Exception as e:
            print(f"Error processing {url}: {e}")
