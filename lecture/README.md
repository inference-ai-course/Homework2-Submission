# Class 2 Lecture: From Transformers to Alignment

This folder contains the main lecture notebook for Week 2 of the Machine Learning Engineer in the Generative AI Era course. The focus is on understanding transformer architecture, attention mechanisms, next-token prediction, and modern alignment techniques (DPO, PPO). You will also learn about inference optimization with quantization (O1, O3).

---

## Contents

- [`lecture.ipynb`](./lecture.ipynb): Step-by-step notebook covering all lecture topics.
- Example code for NumPy attention, PyTorch transformer blocks, Hugging Face LLM inference, and alignment loss functions.

---

## Learning Objectives

- Understand attention mechanisms and implement self-attention in NumPy.
- Build a simple transformer block in PyTorch.
- Run next-token prediction using Hugging Face models.
- Analyze hallucinations and model outputs.
- Explore supervised fine-tuning logic.
- Compare DPO and PPO alignment techniques.
- Optimize inference with quantization (FP16/O1/O3).

---

## Topics Covered

1. **Attention Mechanism (Self-Attention)**
   - Matrix operations for Q, K, V
   - Scaled dot-product attention and softmax

2. **Mini Transformer Block in PyTorch**
   - Multi-head attention, feed-forward network, residuals, and normalization

3. **Next Token Prediction with Hugging Face**
   - Loading and running open-source LLMs (e.g., Mistral-7B)
   - Device selection: CUDA, MPS, or CPU

4. **Alignment: DPO vs PPO**
   - Direct Preference Optimization (DPO) loss
   - Proximal Policy Optimization (PPO) loss
   - Side-by-side code and conceptual comparison

5. **Inference Optimization**
   - FP16 and mixed-precision (O1) for faster, memory-efficient inference
   - Quantization and advanced optimizations (O3)

---

## How to Use

1. Open [`lecture.ipynb`](./lecture.ipynb) in Jupyter or VS Code.
2. Follow the notebook cells in order. Each section includes code, explanations, and discussion prompts.
3. Experiment with device selection and model inference on your hardware.
4. Review the alignment loss examples and compare DPO vs PPO.
5. Try the bonus quantization section for advanced inference optimization.

---

## Requirements

- Python 3.8+
- `numpy`, `torch`, `transformers`, `huggingface_hub`, `dotenv`, `accelerate`
- (Optional) GPU or Apple Silicon for faster inference

Install dependencies with:

```
pip install numpy torch transformers huggingface_hub dotenv accelerate
```

---

Happy learning!