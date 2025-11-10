import os
import json
import subprocess
import whisper
from PIL import Image
import pytesseract

# ------------------- 配置 -------------------
links_file = r"D:\MLE\Homework2-Submission\links.txt"
download_folder = r"D:\MLE\Homework2-Submission\outputs"
originals_folder = os.path.join(download_folder, "originals")
frames_folder = os.path.join(download_folder, "frames")
transcript_path = os.path.join(download_folder, "talks_transcripts.jsonl")

os.makedirs(originals_folder, exist_ok=True)
os.makedirs(frames_folder, exist_ok=True)

# 添加 FFmpeg 到 PATH
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-7.1.1-essentials_build\bin"

# ------------------- 步骤①：用 yt-dlp 下载音频 + 视频 -------------------
def download_audio_and_video(link):
    """
    下载 MP3 和安全命名的 MP4 视频
    """
    print(f"📥 正在下载: {link}")
    try:
        # 下载音频 MP3
        subprocess.run([
            "yt-dlp",
            "-x", "--audio-format", "mp3", "-k",
            "--restrict-filenames",
            "-o", os.path.join(originals_folder, "%(title)s.%(ext)s"),
            link
        ], check=True, text=True)

        # 下载合并视频 MP4（最佳视频 + 音频）
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "--restrict-filenames",
            "-o", os.path.join(originals_folder, "%(title)s.mp4"),
            link
        ], check=True, text=True)

        # 查找最新的 MP3 和 MP4
        mp3_files = [os.path.join(originals_folder, f) for f in os.listdir(originals_folder) if f.endswith(".mp3")]
        video_files = [os.path.join(originals_folder, f) for f in os.listdir(originals_folder) if f.endswith(".mp4")]

        audio_path = max(mp3_files, key=os.path.getmtime) if mp3_files else None
        video_path = max(video_files, key=os.path.getmtime) if video_files else None

        if not audio_path:
            print(f"⚠️ 没找到音频文件 (MP3): {link}")
        if not video_path:
            print(f"⚠️ 没找到视频文件 (MP4): {link}")

        return audio_path, video_path

    except subprocess.CalledProcessError as e:
        print(f"❌ yt-dlp 执行失败: {e}")
        return None, None

# ------------------- 步骤②：Whisper 转录 -------------------
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    print(f"🎧 正在转录: {audio_path}")
    return model.transcribe(audio_path)

# ------------------- 步骤③：OCR 识别视频帧 -------------------
def extract_text_from_video(video_path, frames_dir):
    if not video_path or not os.path.exists(video_path):
        print(f"⚠️ Video not found or invalid path: {video_path}")
        return ""

    os.makedirs(frames_dir, exist_ok=True)

    # 清空旧帧
    for f in os.listdir(frames_dir):
        try:
            os.remove(os.path.join(frames_dir, f))
        except:
            pass

    frame_pattern = os.path.join(frames_dir, "frame_%03d.jpg")

    # 抽帧
    extract_cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps=1/30",
        frame_pattern,
        "-hide_banner", "-loglevel", "error"
    ]
    result = subprocess.run(extract_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ ffmpeg failed to extract frames: {result.stderr}")
        return ""

    # OCR 每张帧
    ocr_texts = []
    for frame_file in sorted(os.listdir(frames_dir)):
        if frame_file.lower().endswith((".jpg", ".png")):
            image_path = os.path.join(frames_dir, frame_file)
            text = pytesseract.image_to_string(Image.open(image_path))
            if text.strip():
                ocr_texts.append(f"[{frame_file}]\n{text.strip()}")

    return "\n\n".join(ocr_texts)

# ------------------- 主流程 -------------------
with open(links_file, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

with open(transcript_path, "w", encoding="utf-8") as out_f:
    for link in links:
        audio_path, video_path = download_audio_and_video(link)
        if not audio_path:
            continue

        whisper_result = transcribe_audio(audio_path)
        ocr_text = extract_text_from_video(video_path, frames_folder) if video_path else ""

        record = {
            "url": link,
            "audio_file": audio_path,
            "video_file": video_path,
            "text": whisper_result["text"],
            "segments": whisper_result["segments"],
            "ocr_text": ocr_text
        }
        out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"✅ 完成: {link}\n")

print("🎯 所有任务已完成，结果保存到 talks_transcripts.jsonl")
