# README – Week 2 Homework Submission  
**MLE in GenAI – Week 2: OCR with Tesseract and Python**  
**Author:** Wei Yang  
**Notebook:** `Wei_Yang_week2_submission.ipynb`

---

## 🔍 Overview

This Week 2 homework focuses on building an **OCR (Optical Character Recognition)** pipeline in Python using:

- **Tesseract OCR engine**
- **pytesseract** (Python bindings for Tesseract)
- **Pillow** for image loading & basic manipulation
- **OpenCV** for image preprocessing

The goal is to extract text from images (including English and Chinese) and improve OCR quality through preprocessing.

---

## 🧩 Homework Objectives

The notebook implements the Week 2 requirements:

### ✔️ 1. Environment & Tesseract Setup
- Installed and configured **Tesseract** on the local machine.
- Verified Tesseract installation from Python using `pytesseract.get_tesseract_version()`.
- Confirmed OCR works on a simple test image.

### ✔️ 2. Basic OCR on English Text
- Loaded test images using **Pillow** / **OpenCV**.
- Ran `pytesseract.image_to_string` on raw images.
- Printed raw OCR outputs and briefly discussed correctness / common errors.

### ✔️ 3. OCR on Chinese Text
- Enabled appropriate **language packs** for Chinese OCR.
- Demonstrated OCR on:
  - Simplified Chinese
  - (Optionally) Traditional Chinese
- Compared recognition quality vs English OCR and noted differences.

### ✔️ 4. Image Preprocessing Pipeline
Implemented preprocessing steps to improve OCR accuracy, such as:

- Grayscale conversion
- Resizing / scaling
- Thresholding or binarization
- Denoising / blurring
- (Optional) morphological operations

Demonstrated how each step changes the image and affects OCR results.

### ✔️ 5. End-to-End OCR Pipeline
- Wrapped the preprocessing + OCR steps into reusable helper functions.
- Ran the full pipeline on multiple example images.
- Displayed both the **preprocessed images** and the **final extracted text**.

---

## 📂 Notebook Structure

| Section | Description |
|--------|-------------|
| **Setup & Imports** | Tesseract path configuration, library imports |
| **Sanity Check: Basic OCR** | Quick OCR test on a simple English image |
| **Chinese OCR Examples** | Applying Tesseract to Chinese text images |
| **Preprocessing Functions** | Grayscale, resize, threshold, denoise, etc. |
| **Improved OCR Results** | Comparing raw vs preprocessed OCR outputs |
| **Summary & Discussion** | Notes on accuracy, limitations, and next steps |

---

## 🛠️ How to Run This Notebook

1. **Install Tesseract**

   - Windows: install from the official Tesseract installer  
   - Make sure the `tesseract` binary is on your PATH, or set the path in Python:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```

2. **Install Python Dependencies**

   In your course environment (e.g. `mle_genai`):

   ```bash
   pip install pytesseract pillow opencv-python
