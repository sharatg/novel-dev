import ollama
import json
import requests
import traceback
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from ..utils.logger import logger

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
            logger.debug(f"Generating text with model: {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} chars")
            logger.debug(f"Temperature: {temperature}, Max tokens: {max_tokens}")

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                logger.debug(f"System prompt length: {len(system_prompt)} chars")
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"Sending request to Ollama at {self.host}")
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens or -1
                }
            )

            content = response['message']['content']
            logger.debug(f"Generated response length: {len(content)} chars")
            return content

        except Exception as e:
            error_msg = f"LLM generation failed with model '{self.model}' at {self.host}"
            logger.error(f"{error_msg}: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Prompt was: {prompt[:200]}..." if len(prompt) > 200 else f"Prompt was: {prompt}")
            raise Exception(f"{error_msg}: {str(e)}")

    def generate_structured(self, prompt: str, schema: Dict[str, Any],
                          system_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            logger.debug("Generating structured response")
            logger.debug(f"Schema keys: {list(schema.get('properties', {}).keys())}")

            json_prompt = f"{prompt}\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"

            if system_prompt:
                full_system = f"{system_prompt}\n\nIMPORTANT: Your response must be valid JSON only, no additional text."
            else:
                full_system = "IMPORTANT: Your response must be valid JSON only, no additional text."

            response = self.generate(json_prompt, full_system, temperature=0.3)
            logger.debug(f"Raw LLM response: {response[:500]}...")

            try:
                parsed = json.loads(response.strip())
                logger.debug("Successfully parsed JSON response")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parsing failed: {e}")
                logger.debug("Attempting to extract JSON from response")
                cleaned = self._extract_json(response)
                logger.debug(f"Extracted JSON: {cleaned[:500]}...")
                parsed = json.loads(cleaned)
                logger.debug("Successfully parsed extracted JSON")
                return parsed

        except Exception as e:
            logger.error(f"Structured generation failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Schema was: {json.dumps(schema, indent=2)}")
            logger.error(f"Response was: {response if 'response' in locals() else 'No response generated'}")
            raise Exception(f"Structured generation failed: {str(e)}")

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