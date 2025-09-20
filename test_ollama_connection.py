#!/usr/bin/env python3
"""
Quick test script to diagnose Ollama connection issues
"""

import sys
import os
sys.path.append('src')

from src.core.llm_interface import LLMInterface

def test_ollama_connection():
    print("🔍 Testing Ollama connection...")

    llm = LLMInterface()
    print(f"Host: {llm.host}")
    print(f"Model: {llm.model}")

    print("\n📋 Checking if Ollama is available...")
    if llm.is_available():
        print("✅ Ollama is available!")

        print("\n🧪 Testing simple generation...")
        try:
            response = llm.generate("Say hello in one word", temperature=0.1)
            print(f"✅ Generation test successful: '{response.strip()}'")
        except Exception as e:
            print(f"❌ Generation test failed: {e}")
    else:
        print("❌ Ollama is not available!")

        print("\n🔧 Troubleshooting suggestions:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check your models: ollama list")
        print("3. Try pulling the default model: ollama pull llama3.1:8b")
        print("4. Check if Ollama is on a different port")

if __name__ == "__main__":
    test_ollama_connection()