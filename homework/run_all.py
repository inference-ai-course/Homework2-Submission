#!/usr/bin/env python3
"""
run_all.py
Main runner script to execute all homework modules sequentially.
Christine Zhao
2025-11-02
"""

import os
import sys
import time
from pathlib import Path


def print_banner(text):
    """Print a formatted banner."""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def run_module(module_name, script_path, description):
    """
    Run a homework module.

    Args:
        module_name: Name of the module
        script_path: Path to the Python script
        description: Brief description of what the module does
    """
    print_banner(f"MODULE: {module_name}")
    print(f"Description: {description}\n")
    print(f"Running: {script_path}\n")

    if not os.path.exists(script_path):
        print(f"ERROR: Script not found at {script_path}")
        return False

    # Change to the script's directory
    original_dir = os.getcwd()
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)

    try:
        # Import and run the module
        script_name = os.path.basename(script_path).replace('.py', '')

        # Add the directory to Python path
        sys.path.insert(0, script_dir)

        # Import the module
        module = __import__(script_name)

        # Run the main function
        if hasattr(module, 'main'):
            start_time = time.time()
            module.main()
            elapsed_time = time.time() - start_time

            print(f"\n✓ Module completed in {elapsed_time:.2f} seconds")
            return True
        else:
            print(f"ERROR: No main() function found in {script_name}")
            return False

    except Exception as e:
        print(f"ERROR running module: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Return to original directory
        os.chdir(original_dir)


def check_dependencies():
    """Check if required dependencies are installed."""
    print_banner("CHECKING DEPENDENCIES")

    missing_packages = []
    required_packages = [
        'requests',
        'bs4',
        'trafilatura',
        'pytesseract',
        'PIL',
        'pdf2image',
        'whisper',
        'langdetect',
        'datasketch'
    ]

    for package in required_packages:
        try:
            if package == 'bs4':
                __import__('bs4')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT FOUND")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print("  pip install -r requirements.txt\n")
        return False

    # Check system dependencies
    print("\nChecking system dependencies...")

    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR")
    except Exception:
        print("✗ Tesseract OCR - NOT FOUND")
        print("  Install: brew install tesseract (macOS)")
        print("  Install: apt install tesseract-ocr (Linux)")
        return False

    # Check yt-dlp
    import subprocess
    try:
        result = subprocess.run(['yt-dlp', '--version'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ yt-dlp")
        else:
            print("✗ yt-dlp - NOT FOUND")
            print("  Install: pip install yt-dlp")
            return False
    except FileNotFoundError:
        print("✗ yt-dlp - NOT FOUND")
        print("  Install: pip install yt-dlp")
        return False

    print("\n✓ All dependencies satisfied!\n")
    return True


def main():
    """Main function to run all modules."""
    print_banner("HOMEWORK 2: DATA COLLECTION & EXTRACTION")
    print("This script will run all four homework modules sequentially.\n")

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        return

    # Get the base directory
    base_dir = Path(__file__).parent  

    # Define modules
    modules = [
        {
            "name": "Module 1 - arXiv Scraper",
            "path": base_dir / "module1_scraper" / "arxiv_scraper.py",
            "description": "Scrapes 200 papers from arXiv and extracts abstracts"
        },
        {
            "name": "Module 2 - PDF OCR",
            "path": base_dir / "module2_pdf_ocr" / "pdf_ocr.py",
            "description": "Converts arXiv PDFs to text using OCR"
        },
        {
            "name": "Module 3 - YouTube ASR",
            "path": base_dir / "module3_asr" / "youtube_transcriber.py",
            "description": "Transcribes YouTube videos using Whisper"
        },
        {
            "name": "Module 4 - Data Cleaning",
            "path": base_dir / "module4_cleaning" / "data_cleaner.py",
            "description": "Cleans and deduplicates data from all modules"
        }
    ]

    # Track results
    results = []

    # Run each module
    start_time = time.time()

    for i, module in enumerate(modules, 1):
        print(f"\n[{i}/{len(modules)}] Starting {module['name']}...")

        success = run_module(
            module['name'],
            str(module['path']),
            module['description']
        )

        results.append({
            'name': module['name'],
            'success': success
        })

        if not success:
            print(f"\n⚠ {module['name']} encountered errors.")
            user_input = input("Continue with remaining modules? (y/n): ")
            if user_input.lower() != 'y':
                break

    # Print summary
    total_time = time.time() - start_time

    print_banner("EXECUTION SUMMARY")

    for result in results:
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"{status}: {result['name']}")

    print(f"\nTotal execution time: {total_time:.2f} seconds")

    # Count successes
    successes = sum(1 for r in results if r['success'])
    print(f"Completed: {successes}/{len(results)} modules\n")

    if successes == len(results):
        print("🎉 All modules completed successfully!")
        print("\nGenerated outputs:")
        print("  - module1_scraper/arxiv_clean.json")
        print("  - module2_pdf_ocr/pdf_ocr/*.txt")
        print("  - module3_asr/talks_transcripts.jsonl")
        print("  - module4_cleaning/clean_corpus.txt")
        print("  - module4_cleaning/stats.md")
    else:
        print("⚠ Some modules failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Execution interrupted by user.")
        sys.exit(1)
