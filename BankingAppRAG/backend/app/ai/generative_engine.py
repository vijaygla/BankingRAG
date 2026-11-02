import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# Model alias mappings to ensure seamless compatibility with Generative Engine
MODEL_MAP = {
    "openai.gpt-5": "openai.gpt-5",
    "openai.gpt-4o": "openai.gpt-4o",
    "anthropic.claude-opus-4-6-v1": "anthropic.claude-opus-5",
    "grok-4": "grok-4"
}

class GenerativeEngineClient:
    def __init__(self):
        self.endpoint = settings.CAPGEMINI_AI_ENDPOINT.rstrip("/")
        self.api_key = settings.CAPGEMINI_AI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> Tuple[str, int, str]:
        """
        Calls Generative Engine chat completions endpoint.
        Returns: (content_text, total_tokens, resolved_model_name)
        """
        chosen_model = model or settings.DEFAULT_AI_MODEL
        resolved_model = MODEL_MAP.get(chosen_model, chosen_model)
        
        payload = {
            "model": resolved_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.endpoint}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                total_tokens = data.get("usage", {}).get("total_tokens", 0)
                return content, total_tokens, resolved_model
            except Exception as e:
                logger.error(f"Generative Engine Chat Error ({resolved_model}): {str(e)}")
                # If chosen model fails, fallback to openai.gpt-4o or default
                if resolved_model != "openai.gpt-4o":
                    try:
                        payload["model"] = "openai.gpt-4o"
                        response = await client.post(
                            f"{self.endpoint}/chat/completions",
                            headers=self.headers,
                            json=payload
                        )
                        response.raise_for_status()
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        total_tokens = data.get("usage", {}).get("total_tokens", 0)
                        return content, total_tokens, "openai.gpt-4o"
                    except Exception as fallback_err:
                        logger.error(f"Fallback Error: {fallback_err}")
                        raise fallback_err
                raise e

    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generates vector embedding for input text using Capgemini Generative Engine.
        """
        embedding_model = model or settings.EMBEDDING_MODEL
        payload = {
            "input": text,
            "model": embedding_model
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.endpoint}/embeddings",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"Generative Engine Embeddings Error: {str(e)}")
                raise e

ai_client = GenerativeEngineClient()
