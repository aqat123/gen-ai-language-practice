from pathlib import Path
from typing import Dict, List
import os

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.ai_services import reset_llm_client

from app.services.image_client import reset_image_client
from app.services.stt_client import reset_stt_client


router = APIRouter()


class ModelListRequest(BaseModel):
    provider: str = Field(..., min_length=2)
    api_key: str = Field(..., min_length=8)


class ModelListResponse(BaseModel):
    provider: str
    models: List[str]


class ApplyConfigRequest(BaseModel):
    provider: str = Field(..., min_length=2)
    api_key: str = Field(..., min_length=8)
    model: str = Field(..., min_length=1)
    image_provider: str | None = None
    image_api_key: str | None = None
    image_model: str | None = None
    stt_provider: str | None = None
    stt_api_key: str | None = None
    stt_model: str | None = None


PROVIDER_CONFIG: Dict[str, Dict[str, str]] = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "auth": "query_key"
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models_url": "https://api.openai.com/v1/models",
        "auth": "bearer"
    },
    "gpt": {
        "base_url": "https://api.openai.com/v1",
        "models_url": "https://api.openai.com/v1/models",
        "auth": "bearer"
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models_url": "https://api.groq.com/openai/v1/models",
        "auth": "bearer"
    }
}


def _normalize_model_name(provider: str, raw_name: str) -> str:
    if provider == "gemini" and raw_name.startswith("models/"):
        return raw_name.split("/", 1)[1]
    return raw_name


def _extract_models(provider: str, payload: Dict) -> List[str]:
    if provider == "gemini":
        models = payload.get("models", [])
        return [_normalize_model_name(provider, model.get("name", "")) for model in models if model.get("name")]
    if provider in {"openai", "gpt", "groq"}:
        models = payload.get("data", [])
        return [model.get("id", "") for model in models if model.get("id")]
    return []


def _update_env_file(env_path: Path, updates: Dict[str, str]) -> None:
    existing_lines: List[str] = []
    if env_path.exists():
        existing_lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_keys = set()
    new_lines: List[str] = []
    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        key, sep, _value = line.partition("=")
        if sep and key in updates:
            new_lines.append(f"{key}={updates[key]}")
            updated_keys.add(key)
        else:
            new_lines.append(line)

    for key, value in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


@router.post("/models", response_model=ModelListResponse)
async def list_models(payload: ModelListRequest) -> ModelListResponse:
    provider = payload.provider.lower().strip()
    provider_config = PROVIDER_CONFIG.get(provider)
    if not provider_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

    headers: Dict[str, str] = {"Accept": "application/json"}
    params: Dict[str, str] = {}
    if provider_config["auth"] == "query_key":
        params["key"] = payload.api_key
    elif provider_config["auth"] == "bearer":
        headers["Authorization"] = f"Bearer {payload.api_key}"
    elif provider_config["auth"] == "anthropic":
        headers["x-api-key"] = payload.api_key
        headers["anthropic-version"] = "2023-06-01"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(provider_config["models_url"], headers=headers, params=params)

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch models for this key")

    data = response.json()
    models = _extract_models(provider, data)
    if not models:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No models found for this key")

    return ModelListResponse(provider=provider, models=sorted(models))


@router.post("/apply")
async def apply_config(payload: ApplyConfigRequest) -> Dict[str, str]:
    provider = payload.provider.lower().strip()
    provider_config = PROVIDER_CONFIG.get(provider)
    if not provider_config:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

    model_name = _normalize_model_name(provider, payload.model.strip())
    base_url = provider_config["base_url"]

    updates = {
        "LLM_PROVIDER": provider,
        "LLM_API_KEY": payload.api_key,
        "LLM_API_BASE_URL": base_url,
        "LLM_MODEL": model_name
    }

    if payload.image_provider and payload.image_api_key and payload.image_model:
        image_provider = payload.image_provider.lower().strip()
        image_config = PROVIDER_CONFIG.get(image_provider)
        if not image_config:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image provider")
        updates.update({
            "LLM_IMAGE_PROVIDER": image_provider,
            "LLM_IMAGE_API_KEY": payload.image_api_key,
            "LLM_IMAGE_API_BASE_URL": image_config["base_url"],
            "LLM_IMAGE_MODEL": payload.image_model.strip()
        })

    if payload.stt_provider and payload.stt_api_key and payload.stt_model:
        stt_provider = payload.stt_provider.lower().strip()
        stt_config = PROVIDER_CONFIG.get(stt_provider)
        if not stt_config:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported STT provider")
        updates.update({
            "STT_PROVIDER": stt_provider,
            "STT_API_KEY": payload.stt_api_key,
            "STT_API_BASE_URL": stt_config["base_url"],
            "STT_MODEL": payload.stt_model.strip()
        })

    env_path = Path(__file__).resolve().parents[4] / ".env"
    _update_env_file(env_path, updates)

    os.environ.update(updates)
    settings.LLM_PROVIDER = provider
    settings.LLM_API_KEY = payload.api_key
    settings.LLM_API_BASE_URL = base_url
    settings.LLM_MODEL = model_name
    if "LLM_IMAGE_PROVIDER" in updates:
        settings.LLM_IMAGE_PROVIDER = updates["LLM_IMAGE_PROVIDER"]
        settings.LLM_IMAGE_API_KEY = updates["LLM_IMAGE_API_KEY"]
        settings.LLM_IMAGE_API_BASE_URL = updates["LLM_IMAGE_API_BASE_URL"]
        settings.LLM_IMAGE_MODEL = updates["LLM_IMAGE_MODEL"]
    if "STT_PROVIDER" in updates:
        settings.STT_PROVIDER = updates["STT_PROVIDER"]
        settings.STT_API_KEY = updates["STT_API_KEY"]
        settings.STT_API_BASE_URL = updates["STT_API_BASE_URL"]
        settings.STT_MODEL = updates["STT_MODEL"]

    reset_llm_client()
    reset_image_client()
    reset_stt_client()

    return {
        "status": "ok",
        "provider": provider,
        "model": model_name
    }