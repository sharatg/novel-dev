import ollama
import json
import requests
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        # Try different client initialization methods
        try:
            self.client = ollama.Client(host=self.host)
        except:
            # Fallback to default client
            self.client = ollama.Client()

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens or -1
                }
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def generate_structured(self, prompt: str, schema: Dict[str, Any],
                          system_prompt: Optional[str] = None) -> Dict[str, Any]:
        json_prompt = f"{prompt}\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"

        if system_prompt:
            full_system = f"{system_prompt}\n\nIMPORTANT: Your response must be valid JSON only, no additional text."
        else:
            full_system = "IMPORTANT: Your response must be valid JSON only, no additional text."

        response = self.generate(json_prompt, full_system, temperature=0.3)

        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            cleaned = self._extract_json(response)
            return json.loads(cleaned)

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx + 1]
        raise ValueError("No valid JSON found in response")

    def is_available(self) -> bool:
        try:
            # First check if Ollama server is reachable via HTTP
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Ollama server not reachable at {self.host}")
                return False

            # Try to get models using the client
            try:
                models = self.client.list()
                available_models = [model['name'] for model in models['models']]
            except:
                # Fallback: try direct API call
                models_response = requests.get(f"{self.host}/api/tags", timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    available_models = [model['name'] for model in models_data.get('models', [])]
                else:
                    print("Could not retrieve model list from Ollama")
                    return False

            print(f"Available models: {available_models}")

            # Check for exact match first
            if self.model in available_models:
                print(f"✅ Found exact match for model: {self.model}")
                return True

            # Check for partial matches (e.g., "llama3.1:8b" might be listed as "llama3.1")
            model_base = self.model.split(':')[0]
            for available_model in available_models:
                if model_base in available_model or available_model.startswith(model_base):
                    print(f"✅ Found compatible model: {available_model} for requested {self.model}")
                    # Update our model to use the available one
                    self.model = available_model
                    return True

            print(f"❌ Model '{self.model}' not found. Available models: {available_models}")
            print(f"💡 Try: ollama pull {self.model}")
            return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {self.host}: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Unexpected error checking Ollama: {e}")
            return False