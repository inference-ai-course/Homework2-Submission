"""
Unified LLM Client for Claude API and Ollama

This module provides a single interface for interacting with both
cloud-based (Claude) and local (Ollama) language models.

Default models:
  - Path A (Claude): claude-sonnet-4-6
  - Path B (Ollama): qwen3.5:27b
"""

import os
import requests
from typing import Dict, List, Optional, Any
from google import genai
from google.genai import types

class LLMClient:
    """Unified client for interacting with LLMs (Claude or Ollama)"""

    # Default model names
    DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-6" #  claude-haiku-4-5-20251001
    DEFAULT_OLLAMA_MODEL = "llama3.2:latest"#qwen3.5:27b
    DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview" # Path D gemini-2.5-flash   
    def __init__(self, path: str = "A"):
        """
        Initialize the LLM client based on chosen path.

        Args:
            path: "A" for Claude, "B" for Ollama, "C" for Hybrid
        """
        self.path = path
        self.claude_client = None
        self.default_model = None
        self.gemini_model = None

        if path in ["A", "C"]:
            self._init_claude()
        if path in ["B", "C"]:
            self._init_ollama()
        if path == "D":
            self._init_gemini()

    def _init_claude(self):
        """Initialize Claude API client"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            self.claude_client = anthropic.Anthropic(api_key=api_key)
            self.default_model = self.DEFAULT_CLAUDE_MODEL

            print("✓ Claude API client initialized")
            print(f"  Default model: {self.default_model}")
            print(f"  Available: claude-sonnet-4-6, claude-opus-4-6, claude-haiku-4-5-20251001")
        except Exception as e:
            print(f"❌ Failed to initialize Claude: {e}")
            raise
    def _init_gemini(self):
        """Initialize Google Gemini client"""
       
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print("⚠ GOOGLE_API_KEY not found in environment.")
                return

            # NEW 2026 PATTERN: Initialize a Client object
            # The key is passed directly to the Client constructor
            self.gemini_client = genai.Client(api_key=api_key)
            
            # We store the model name string, not the model object itself
            self.default_model = self.DEFAULT_GEMINI_MODEL 
            
            print(f"✓ Gemini client initialized ({self.DEFAULT_GEMINI_MODEL})")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
        # try:
        #     api_key = os.getenv('GOOGLE_API_KEY')
        #     if not api_key:
        #         print("⚠ GOOGLE_API_KEY not found in environment.")
        #         return

        #     genai.configure(api_key=api_key)
        #     self.gemini_model = genai.GenerativeModel(self.DEFAULT_GEMINI_MODEL)
        #     self.default_model = self.DEFAULT_GEMINI_MODEL
        #     print(f"✓ Gemini client initialized ({self.DEFAULT_GEMINI_MODEL})")
        # except Exception as e:
        #     print(f"❌ Failed to initialize Gemini: {e}")

    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]

                # Prefer qwen3.5:27b if available
                if self.DEFAULT_OLLAMA_MODEL in model_names:
                    self.default_model = self.DEFAULT_OLLAMA_MODEL
                elif models:
                    self.default_model = models[0]['name']
                else:
                    print("⚠ Ollama running but no models found")
                    print(f"  Run: ollama pull {self.DEFAULT_OLLAMA_MODEL}")
                    return

                print("✓ Ollama client initialized")
                print(f"  Available models: {model_names}")
                print(f"  Default model: {self.default_model}")
            else:
                raise ConnectionError("Ollama server not responding")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("  Make sure Ollama is running: ollama serve")
            raise

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 1024,
        use_claude: bool = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system: System prompt (optional)
            model: Override default model
            temperature: Randomness (0-1 for Claude, 0-2 for Ollama)
            max_tokens: Maximum response length
            use_claude: For hybrid path, explicitly choose Claude (True) or Ollama (False)

        Returns:
            Dictionary with 'content', 'model', 'usage', 'stop_reason' keys
        """
        # use_claude_backend = False
        # if self.path == "A":
        #     use_claude_backend = True
        # elif self.path == "B":
        #     use_claude_backend = False
        # elif self.path == "C":
        #     use_claude_backend = use_claude if use_claude is not None else True

        # if model is None:
        #     if use_claude_backend:
        #         model = self.DEFAULT_CLAUDE_MODEL
        #     else:
        #         model = self.default_model or self.DEFAULT_OLLAMA_MODEL

        # if use_claude_backend:
        #     return self._generate_claude(prompt, system, model, temperature, max_tokens)
        
        # if self.path == "D":
        #     return self._generate_gemini(prompt, system, model, temperature, max_tokens)
        # else:
        #     return self._generate_ollama(prompt, system, model, temperature, max_tokens)
        
        # # fallback to existing logic
        # return super().generate(prompt, **kwargs) 
        # 1. Determine which BACKEND to use
        selected_path = self.path
        
        # Handle Hybrid (Path C) Logic
        if self.path == "C":
            selected_path = "A" if (use_claude or use_claude is None) else "B"

        # 2. Set the Model if not overridden
        if model is None:
            if selected_path == "A":
                model = self.DEFAULT_CLAUDE_MODEL
            elif selected_path == "B":
                model = self.default_model or self.DEFAULT_OLLAMA_MODEL
            elif selected_path == "D":
                model = self.DEFAULT_GEMINI_MODEL

        # 3. ROUTING (The Traffic Controller)
        if selected_path == "A":
            return self._generate_claude(prompt, system, model, temperature, max_tokens)
        
        elif selected_path == "B":
            return self._generate_ollama(prompt, system, model, temperature, max_tokens)
            
        elif selected_path == "D":
            return self._generate_gemini(prompt, system, model, temperature, max_tokens)
        
        else:
            return {"error": f"Invalid path configuration: {self.path}"}

    def generate_with_thinking(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        budget_tokens: int = 2000,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Generate a response using Claude's extended thinking (Path A/C only).

        Args:
            prompt: The user prompt
            system: System prompt (optional)
            model: Claude model to use
            budget_tokens: Thinking budget in tokens
            max_tokens: Maximum total response tokens (must be > budget_tokens)

        Returns:
            Dictionary with 'content', 'thinking', 'model', 'usage' keys
        """
        if self.path not in ["A", "C"]:
            return {"error": "Extended thinking requires Path A (Claude API) or Path C (Hybrid)"}

        if model is None:
            model = self.DEFAULT_CLAUDE_MODEL

        try:
            kwargs = {
                "model": model,
                "max_tokens": max(max_tokens, budget_tokens + 1024),
                "thinking": {"type": "enabled", "budget_tokens": budget_tokens},
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system

            response = self.claude_client.messages.create(**kwargs)

            thinking_text = ""
            answer_text = ""
            for block in response.content:
                if block.type == "thinking":
                    thinking_text = block.thinking
                elif block.type == "text":
                    answer_text = block.text

            return {
                "content": answer_text,
                "thinking": thinking_text,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }
        except Exception as e:
            return {"error": str(e), "model": model}

    def _generate_claude(self, prompt, system, model, temperature, max_tokens):
        """Generate response using Claude API"""
        try:
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system:
                kwargs["system"] = system

            response = self.claude_client.messages.create(**kwargs)
            return {
                "content": response.content[0].text,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }
        except Exception as e:
            return {"error": str(e), "model": model}
    # def _generate_gemini(self, prompt, system, model, temperature, max_tokens):
    #     try:
    #     # The new SDK 2026 pattern
    #         response = self.gemini_client.models.generate_content(
    #             model=model or "gemini-2.5-flash",
    #             contents=prompt,
    #             config={
    #                 "system_instruction": system,
    #                 "temperature": temperature,
    #                 "max_output_tokens": max_tokens
    #             }
    #         )
    #         return {
    #             "content": response.text,
    #             "model": model or "gemini-2.5-flash",
    #             "usage": {"total_tokens": response.usage_metadata.total_token_count}
    #         }
    #     except Exception as e:
    #         return {"error": str(e)}
    def _generate_gemini(self, prompt, system, model, temperature, max_tokens):
        print("⚡ Generating with Gemini...")
        try:
            response = self.gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )

            stop_reason = None
            if response.candidates:
                stop_reason = response.candidates[0].finish_reason

            return {
                "content": response.text,
                "model": model or self.default_model,
                "stop_reason": str(stop_reason),
                "usage": {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_ollama(self, prompt, system, model, temperature, max_tokens):
        """Generate response using Ollama (chat API)"""
        import re

        try:
            # Build chat messages (chat API handles system prompt properly
            # and works correctly with qwen3.5 thinking models)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        # qwen3.5 uses hidden thinking tokens that count against
                        # num_predict, so we need a larger budget to get visible output
                        "num_predict": max_tokens * 4 if "qwen3" in model.lower() else max_tokens,
                        "temperature": temperature,
                    },
                },
                timeout=300,
            )

            if response.status_code == 200:
                data = response.json()
                raw_content = data.get('message', {}).get('content', '')

                # Strip any <think>...</think> blocks from thinking models
                content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
                if not content:
                    content = raw_content.strip()

                return {
                    "content": content,
                    "model": model,
                    "usage": {
                        "input_tokens": data.get('prompt_eval_count', 0),
                        "output_tokens": data.get('eval_count', 0),
                    },
                    "stop_reason": "complete",
                }
            else:
                return {"error": f"HTTP {response.status_code}", "model": model}

        except Exception as e:
            return {"error": str(e), "model": model}

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = []

        if self.path in ["A", "C"]:
            models.extend([
                "claude-sonnet-4-6",
                "claude-opus-4-6",
                "claude-haiku-4-5-20251001",
            ])

        if self.path in ["B", "C"]:
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    ollama_models = [m['name'] for m in response.json().get('models', [])]
                    models.extend(ollama_models)
            except Exception:
                pass

        return models


    

    # def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
    #     # ... (keep your existing Path A/B/C logic) ...
        
    #     if self.path == "D":
    #         return self._generate_gemini(prompt, **kwargs)
        
    #     # fallback to existing logic
    #     return super().generate(prompt, **kwargs) 

    
