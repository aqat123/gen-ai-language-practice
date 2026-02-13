import httpx
import base64
import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.ai_services import get_llm_client


class STTError(Exception):
    """Custom exception for STT-related errors."""
    pass


class STTClient:
    """Client for Speech-to-Text API plus phonetic analysis."""

    def __init__(self, api_key: str, base_url: str, model: str, provider: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.model = model
        self.provider = provider.lower()

    async def analyze_audio(
            self,
            audio_bytes: bytes,
            mime_type: str = "audio/webm",
            target_language: str = "English",
            target_phrase: str = ""
    ) -> Dict[str, Any]:
        """
        Transcribes audio AND provides phonetic feedback in one go.
        """
        try:
            if self.provider in {"openai", "gpt"}:
                return await self._analyze_openai_compatible(
                    audio_bytes=audio_bytes,
                    mime_type=mime_type,
                    target_language=target_language,
                    target_phrase=target_phrase
                )
            if self.provider == "groq":
                return await self._analyze_groq(
                    audio_bytes=audio_bytes,
                    mime_type=mime_type,
                    target_language=target_language,
                    target_phrase=target_phrase
                )

            return await self._analyze_gemini(
                audio_bytes=audio_bytes,
                mime_type=mime_type,
                target_language=target_language,
                target_phrase=target_phrase
            )

        except httpx.HTTPError as e:
            raise STTError(f"HTTP error during STT API call: {str(e)}")
        except json.JSONDecodeError:
            raise STTError("AI returned invalid JSON")
        except Exception as e:
            raise STTError(f"Error during speech transcription: {str(e)}")

    async def _analyze_groq(
            self,
            audio_bytes: bytes,
            mime_type: str,
            target_language: str,
            target_phrase: str
    ) -> Dict[str, Any]:
        return await self._analyze_openai_compatible(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            target_language=target_language,
            target_phrase=target_phrase
        )

    async def _analyze_gemini(
            self,
            audio_bytes: bytes,
            mime_type: str,
            target_language: str,
            target_phrase: str
    ) -> Dict[str, Any]:
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        prompt_text = f"""
            You are a strict {target_language} phonetic expert. 
            The user is trying to say: "{target_phrase}"

            Task 1: Transcribe the audio exactly.
            Task 2: Analyze the user's pronunciation, accent, and fluency.

            Respond ONLY with valid JSON in this format:
            {{
                "transcript": "The exact text spoken",
                "confidence": 0.92,
                "score": 85,
                "feedback": "Overall comment on accent and clarity",
                "word_level_feedback": [
                    {{
                        "word": "word_spoken",
                        "issue": "What was wrong (e.g., 'th' sound was 'z')",
                        "tip": "How to fix it (e.g., 'Place tongue between teeth')"
                    }}
                ]
            }}
            """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": b64_audio
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                raw_text = candidate["content"]["parts"][0]["text"]
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]

                parsed_result = json.loads(clean_json)
                if "confidence" not in parsed_result:
                    parsed_result["confidence"] = 1.0
                if "word_level_feedback" not in parsed_result:
                    parsed_result["word_level_feedback"] = []
                return parsed_result
        raise STTError("No content returned from AI")

    async def _analyze_openai_compatible(
            self,
            audio_bytes: bytes,
            mime_type: str,
            target_language: str,
            target_phrase: str
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        files = {
            "file": ("audio.webm", audio_bytes, mime_type)
        }
        data = {
            "model": self.model
        }

        response = await self.client.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        payload = response.json()
        transcript = payload.get("text", "")

        llm = get_llm_client()
        prompt_text = f"""
            You are a strict {target_language} phonetic expert.
            The user is trying to say: "{target_phrase}"

            Task 1: Use this transcript as the user's spoken words.
            Transcript: "{transcript}"
            Task 2: Analyze pronunciation, accent, and fluency.

            Respond ONLY with valid JSON in this format:
            {{
                "transcript": "The exact text spoken",
                "confidence": 0.92,
                "score": 85,
                "feedback": "Overall comment on accent and clarity",
                "word_level_feedback": [
                    {{
                        "word": "word_spoken",
                        "issue": "What was wrong",
                        "tip": "How to fix it"
                    }}
                ]
            }}
            """

        analysis = await llm.generate(
            system_prompt="You are a strict phonetic evaluator. Respond with JSON only.",
            user_prompt=prompt_text,
            temperature=0.2,
            max_tokens=512
        )

        clean_json = analysis.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]

        parsed_result = json.loads(clean_json)
        if "transcript" not in parsed_result:
            parsed_result["transcript"] = transcript
        if "confidence" not in parsed_result:
            parsed_result["confidence"] = 1.0
        if "word_level_feedback" not in parsed_result:
            parsed_result["word_level_feedback"] = []
        return parsed_result

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global STT client instance
_stt_client: Optional[STTClient] = None


def reset_stt_client() -> None:
    """Reset the global STT client instance after config changes."""
    global _stt_client
    _stt_client = None


def get_stt_client() -> STTClient:
    """Get or create the global STT client instance."""
    global _stt_client
    if _stt_client is None:
        _stt_client = STTClient(
            api_key=settings.STT_API_KEY,
            base_url=settings.STT_API_BASE_URL,
            model=settings.STT_MODEL,
            provider=settings.STT_PROVIDER
        )
    return _stt_client
