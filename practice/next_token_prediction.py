
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import torch

# Optional if already logged in via CLI
# login(token="your_hf_token")

# Check device for MacBook (MPS if available, else CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load tokenizer and model with Hugging Face gated repo access
tokenizer = AutoTokenizer.from_pretrained(model_name, token=True)
model = AutoModelForCausalLM.from_pretrained(model_name, token=True).to(device)

# Prepare input prompt
prompt = "The Eiffel Tower is located in"
inputs = tokenizer(prompt, return_tensors="pt").to(device)

# Run generation
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=10)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))