"""LLM completion interface using LiteLLM with built-in resilience and backup strategy."""

import os
import time
import logging
import litellm
from dotenv import load_dotenv

# Load .env at module level so keys are available regardless of entry point
# (MCP server child process, CLI, programmatic API, etc.)
load_dotenv()

logger = logging.getLogger(__name__)


def call_llm(prompt: str, max_tokens: int = 4000) -> str:
    """Call LiteLLM with configured model, API keys, and exponential backoff retry.

    Model selection priority:
      1. MODEL environment variable (e.g. "google/gemini-2.5-pro")
      2. Default: "openai/meta/llama-3.1-8b-instruct" via NVIDIA NIM

    Fallback chain:
      Primary model (3 retries with backoff) → NVIDIA NIM backup
    """
    model_name = os.getenv("MODEL", "openai/meta/llama-3.1-8b-instruct")

    # Normalize legacy model name aliases
    if model_name == "gemini/gemini-1.5-flash" or "1.5-flash" in model_name:
        model_name = "gemini/gemini-flash-latest"

    max_retries = 3
    base_delay = 2.0

    for attempt in range(max_retries):
        try:
            # Configure provider credentials for LiteLLM
            if "gemini" in model_name or "google" in model_name:
                gemini_key = os.getenv("GEMINI_API_KEY", "")
                if not gemini_key:
                    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
                os.environ["GEMINI_API_KEY"] = gemini_key
            else:
                # OpenAI-compatible endpoint (NVIDIA NIM, OpenRouter, etc.)
                api_base = os.getenv("OPENAI_API_BASE", "https://integrate.api.nvidia.com/v1")
                api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY", "")
                os.environ["OPENAI_API_BASE"] = api_base
                os.environ["OPENAI_API_KEY"] = api_key

            logger.info(f"Calling LLM ({model_name}) — Attempt {attempt + 1}/{max_retries}")
            response = litellm.completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                logger.info(f"Retrying in {sleep_time:.1f}s…")
                time.sleep(sleep_time)
            else:
                # Last resort: try NVIDIA NIM backup if not already using it
                nv_key = os.getenv("NVIDIA_API_KEY")
                if nv_key and "nvidia" not in model_name and "llama" not in model_name:
                    logger.info("Attempting backup call via NVIDIA NIM…")
                    try:
                        os.environ["OPENAI_API_BASE"] = "https://integrate.api.nvidia.com/v1"
                        os.environ["OPENAI_API_KEY"] = nv_key
                        response = litellm.completion(
                            model="openai/meta/llama-3.1-8b-instruct",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=max_tokens,
                        )
                        return response.choices[0].message.content or ""
                    except Exception as backup_err:
                        logger.error(f"Backup LLM call also failed: {backup_err}")
                raise RuntimeError(f"LLM call failed after {max_retries} attempts: {e}")
