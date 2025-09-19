import ollama
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        self.client = ollama.Client(host=self.host)

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
            models = self.client.list()
            return any(model['name'] == self.model for model in models['models'])
        except Exception:
            return False