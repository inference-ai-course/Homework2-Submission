# Class 2 Project: Running and Comparing Open-Source LLMs

This project guides you through practical workflows for downloading, running, and benchmarking open-source large language models (LLMs) locally. You will use Hugging Face Transformers, vLLM, and Ollama to compare model outputs, latency, and cost.

## Project Tasks

### 1. Download and Run Open-Source Models
- **Goal:** Use Hugging Face Transformers to download and run models such as Llama 3 or Mistral.
- **Example:**  
  Load `meta-llama/Meta-Llama-3-8B-Instruct` and generate a completion for a prompt.
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype="auto")
  prompt = "The Eiffel Tower is located in"
  inputs = tokenizer(prompt, return_tensors="pt")
  inputs = {k: v.to(model.device) for k, v in inputs.items()}
  outputs = model.generate(**inputs, max_new_tokens=10)
  print(tokenizer.decode(outputs[0], skip_special_tokens=True))
  ```

### 2. Serve Models Locally with vLLM
- **Goal:** Install vLLM and start a local API server for fast inference.
- **Example:**
  ```bash
  pip install vllm --torch-backend=auto
  python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen1.5-1.8B-Chat \
    --gpu-memory-utilization 0.8 \
    --max-model-len 1024 \
    --dtype float16 \
    --api-key token-local
  ```

### 3. Compare Results Across Local APIs
- **Goal:** Use identical prompts to compare outputs, latency, and cost between Hugging Face, vLLM, and Ollama models.
- **Example:**
  ```python
  prompts = [
      "What is the capital of Canada?",
      "Explain the theory of relativity in simple terms.",
      "Write a haiku about autumn in Ontario."
  ]
  # Query each model and print results with timing
  ```

### 4. Evaluate and Document Findings
- **Goal:** Analyze how local models stack up in terms of accuracy, speed, and resource usage.  
- **Tip:** Document your observations and include sample outputs for each model.

---

## Learning Outcomes
- Practice running open-source LLMs locally using different frameworks
- Understand device selection and precision (FP16/FP32) for efficient inference
- Benchmark and compare model outputs and latency
- Gain hands-on experience with local model serving and API integration

Work through each section in the notebook and use the examples as templates for your own experiments and evaluations.