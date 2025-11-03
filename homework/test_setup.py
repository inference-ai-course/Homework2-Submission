#!/usr/bin/env python3
"""
test_setup.py
Quick test script to verify all dependencies are installed correctly.
Christine Zhao
2025-11-02
"""

import sys


def test_import(package_name, import_name=None):
    """Test if a package can be imported."""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError as e:
        print(f"✗ {package_name} - {e}")
        return False


def test_tesseract():
    """Test Tesseract OCR installation."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR (version {version})")
        return True
    except Exception as e:
        print(f"✗ Tesseract OCR - {e}")
        return False


def test_yt_dlp():
    """Test yt-dlp installation."""
    import subprocess
    try:
        result = subprocess.run(['yt-dlp', '--version'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ yt-dlp (version {version})")
            return True
        else:
            print(f"✗ yt-dlp - Command failed")
            return False
    except FileNotFoundError:
        print("✗ yt-dlp - Not found in PATH")
        return False
    except Exception as e:
        print(f"✗ yt-dlp - {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Testing Homework 2 Setup")
    print("="*60 + "\n")

    print("Python Packages:")
    print("-" * 60)

    packages = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("trafilatura", "trafilatura"),
        ("lxml", "lxml"),
        ("pytesseract", "pytesseract"),
        ("Pillow", "PIL"),
        ("pdf2image", "pdf2image"),
        ("openai-whisper", "whisper"),
        ("langdetect", "langdetect"),
        ("datasketch", "datasketch"),
        ("tqdm", "tqdm"),
        ("numpy", "numpy"),
    ]

    results = []
    for package_name, import_name in packages:
        results.append(test_import(package_name, import_name))

    print("\nSystem Dependencies:")
    print("-" * 60)

    results.append(test_tesseract())
    results.append(test_yt_dlp())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("="*60)
        print("\nYou're ready to run the homework modules!")
        print("Run: python run_all.py")
    else:
        print(f"⚠ {total - passed} test(s) failed ({passed}/{total} passed)")
        print("="*60)
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nFor system dependencies:")
        print("  - Tesseract: brew install tesseract (macOS)")
        print("  - yt-dlp: pip install yt-dlp")
        sys.exit(1)


if __name__ == "__main__":
    main()
