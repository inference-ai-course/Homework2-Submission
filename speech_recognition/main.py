import os
from pathlib import Path
from typing import List

import yt_dlp
import glob
from typing import Optional


def list_audio_files(directory: Path) -> List[Path]:
    patterns = [
        "*.m4a",
        "*.mp3",
        "*.wav",
        "*.webm",
        "*.mp4",
        "*.aac",
        "*.flac",
        "*.ogg",
        "*.mkv",
    ]
    files: List[Path] = []
    for pattern in patterns:
        files.extend(Path(directory).glob(pattern))
    # De-duplicate while preserving order
    seen = set()
    unique_files: List[Path] = []
    for f in files:
        if f.resolve() not in seen:
            unique_files.append(f)
            seen.add(f.resolve())
    return unique_files


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def download_audio(urls: List[str], output_dir: Path) -> None:
    ensure_directory(output_dir)

    ydl_opts = {
        # Prefer m4a to avoid requiring ffmpeg for conversion on most systems
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                ydl.download([url])
            except Exception as exc:
                print(f"Failed to download {url}: {exc}")


def transcribe_with_whisper_base(input_dir: Path, output_dir: Path) -> None:
    ensure_directory(output_dir)
    try:
        import whisper  # type: ignore
        import torch  # type: ignore
    except Exception as exc:
        print(
            "Whisper (and torch) are required. Please install with `pip install openai-whisper`.",
        )
        raise

    model = whisper.load_model("base")
    use_fp16 = False
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            use_fp16 = True
    except Exception:
        use_fp16 = False

    audio_files = list_audio_files(input_dir)
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return

    for audio_path in audio_files:
        try:
            print(f"Transcribing: {audio_path.name}")
            result = model.transcribe(str(audio_path), fp16=use_fp16)
            text = result.get("text", "").strip()
            out_txt = output_dir / (audio_path.stem + ".txt")
            out_txt.write_text(text, encoding="utf-8")
        except Exception as exc:
            print(f"Failed to transcribe {audio_path}: {exc}")


if __name__ == "__main__":
    default_urls = [
        "https://www.youtube.com/watch?v=lfJOlp2sN18",
        "https://www.youtube.com/watch?v=068nfPdtssI",
        "https://www.youtube.com/watch?v=nD79Ntzy5vA",
    ]

    output_directory = Path(__file__).resolve().parent / "downloads"
    download_audio(default_urls, output_directory)
    transcripts_directory = Path(__file__).resolve().parent / "transcripts"
    transcribe_with_whisper_base(output_directory, transcripts_directory)


