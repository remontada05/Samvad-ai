"""
Gemini AI Client
Centralized wrapper for Google Gemini API with fallback support
"""

import os
import json
import time
import traceback
import google.generativeai as genai
from typing import Optional, Dict, Any

class GeminiClient:
    """Singleton wrapper for Google Gemini API"""
    
    _instance = None
    _model = None
    _available = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Gemini client with API key"""
        api_key = os.environ.get('GEMINI_API_KEY', '')
        
        if api_key and api_key != 'your_api_key_here':
            try:
                genai.configure(api_key=api_key)
                # Use gemini-2.5-flash for best free-tier performance
                self._model = genai.GenerativeModel('gemini-2.5-flash')
                self._available = True
                print("✅ Gemini AI connected successfully!")
                print("   Model: gemini-2.5-flash | Free tier active")
            except Exception as e:
                print(f"⚠️ Gemini AI initialization failed: {e}")
                self._available = False
        else:
            print("⚠️ No Gemini API key found. Running in fallback mode.")
            print("   Get a free key at: https://aistudio.google.com/apikeys")
            self._available = False
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.8, retries: int = 2) -> Optional[str]:
        """
        Generate text using Gemini API with retry logic for rate limits
        """
        if not self._available:
            return None
        
        for attempt in range(retries + 1):
            try:
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
                
                response = self._model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response and response.text:
                    return response.text.strip()
                print(f"⚠️ Gemini returned empty response (attempt {attempt + 1})")
                return None
                
            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Gemini generate() error (attempt {attempt + 1}/{retries + 1}): {error_str[:200]}")
                
                # If rate limited, wait and retry
                if '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                    if attempt < retries:
                        wait_time = (attempt + 1) * 5  # 5s, 10s
                        print(f"   Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"   Rate limit persists after {retries + 1} attempts. Using fallback.")
                        return None
                else:
                    print(f"   Full error: {traceback.format_exc()}")
                    return None
        
        return None
    
    def generate_json(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7, retries: int = 2) -> Optional[Dict]:
        """
        Generate JSON response from Gemini with retry logic
        """
        if not self._available:
            return None
        
        for attempt in range(retries + 1):
            try:
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    response_mime_type="application/json"
                )
                
                response = self._model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response and response.text:
                    return json.loads(response.text.strip())
                return None
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error: {e}")
                try:
                    text = response.text.strip()
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        return json.loads(text[start:end])
                except:
                    pass
                return None
            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Gemini generate_json() error (attempt {attempt + 1}/{retries + 1}): {error_str[:200]}")
                
                if '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                    if attempt < retries:
                        wait_time = (attempt + 1) * 5
                        print(f"   Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"   Rate limit persists. Using fallback.")
                        return None
                else:
                    print(f"   Full error: {traceback.format_exc()}")
                    return None
        
        return None


# Global singleton instance
gemini = GeminiClient()
