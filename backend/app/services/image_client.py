import httpx
from typing import Optional
from app.core.config import settings

class ImageGenClient:
    """Client dedicated to interacting with Image Generation API (Imagen 4)."""

    def __init__(self, api_key: str, base_url: str, model: str, provider: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.provider = provider.lower()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate_safe_image(self, prompt: str) -> Optional[str]:
        """
        Generate a safe image based on the prompt.
        Returns: base64 encoded image string OR None if generation fails.
        """
        try:
            safe_prompt = (
                f"cartoon style illustration of {prompt}. "
                "minimalist, educational, white background, clear lines, safe for work. "
                "IMPORTANT: No text, letters, or words should appear in the image."
            )

            if self.provider in {"openai", "gpt"}:
                url = f"{self.base_url}/images/generations"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "prompt": safe_prompt,
                    "size": "1024x1024",
                    "response_format": "b64_json"
                }
                response = await self.client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    print(f"IMAGE GEN ERROR: {response.status_code} - {response.text}")
                    return None
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0].get("b64_json")
                return None

            if self.provider == "groq":
                print("IMAGE GEN ERROR: Groq does not support image generation.")
                return None

            # Default to Gemini Imagen REST
            url = f"{self.base_url}/models/{self.model}:predict?key={self.api_key}"
            payload = {
                "instances": [
                    {
                        "prompt": safe_prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "1:1"
                }
            }

            response = await self.client.post(url, json=payload)

            # Print error if it fails so we can debug in terminal
            if response.status_code != 200:
                print(f"IMAGE GEN ERROR: {response.status_code} - {response.text}")
                return None

            data = response.json()

            # Extract Base64 image
            # Imagen 4 usually returns: {"predictions": [{"bytesBase64Encoded": "..."}]}
            if "predictions" in data and len(data["predictions"]) > 0:
                prediction = data["predictions"][0]

                # Check for standard encoding key
                if "bytesBase64Encoded" in prediction:
                    return prediction["bytesBase64Encoded"]

                # Check for alternative key
                if "b64" in prediction:
                    return prediction["b64"]

            return None

        except Exception as e:
            print(f"Image Gen Exception: {e}")
            return None

    async def close(self):
        await self.client.aclose()

_image_client: Optional[ImageGenClient] = None


def reset_image_client() -> None:
    """Reset singleton ImageGenClient instance after config changes."""
    global _image_client
    _image_client = None


def get_image_client() -> ImageGenClient:
    """Get singleton ImageGenClient instance."""
    global _image_client
    if _image_client is None:
        _image_client = ImageGenClient(
            api_key=settings.LLM_IMAGE_API_KEY,
            base_url=settings.LLM_IMAGE_API_BASE_URL,
            model=settings.LLM_IMAGE_MODEL,
            provider=settings.LLM_IMAGE_PROVIDER,
        )
    return _image_client
