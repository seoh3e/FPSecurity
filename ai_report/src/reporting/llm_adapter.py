from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib import request


SYSTEM_PROMPT = "당신은 게임 운영자를 돕는 안티치트 분석 어시스턴트다. 근거 중심의 짧은 한국어 보고서를 작성하라."


def _try_openai(prompt: str, model: str, api_key: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
    )
    text = (response.output_text or "").strip()
    if not text:
        raise RuntimeError("OpenAI returned empty output.")
    return text


def _try_ollama(prompt: str, model: str, base_url: str, timeout_sec: int) -> str:
    final_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
    payload = {
        "model": model,
        "prompt": final_prompt,
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{base_url.rstrip('/')}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
    except HTTPError as http_err:
        body = ""
        try:
            body = http_err.read().decode("utf-8")
        except Exception:
            body = ""
        raise RuntimeError(
            f"Ollama HTTP {http_err.code} at {base_url.rstrip('/')}/api/generate. body={body}"
        ) from http_err
    data = json.loads(raw)
    text = (data.get("response") or "").strip()
    if not text:
        raise RuntimeError("Ollama returned empty output.")
    return text


def generate_llm_report(
    prompt: str,
    model: str = "gpt-4o-mini",
    provider: str = "auto",
    ollama_base_url: str = "http://localhost:11434",
    ollama_timeout_sec: int = 180,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    provider_lower = provider.lower().strip()
    if provider_lower not in {"auto", "openai", "ollama"}:
        raise RuntimeError("Invalid LLM provider. Use one of: auto, openai, ollama.")

    if provider_lower == "openai":
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when provider=openai.")
        try:
            return _try_openai(prompt=prompt, model=model, api_key=api_key)
        except Exception as exc:
            raise RuntimeError("LLM report generation failed with OpenAI.") from exc

    if provider_lower == "ollama":
        try:
            return _try_ollama(prompt=prompt, model=model, base_url=ollama_base_url, timeout_sec=ollama_timeout_sec)
        except Exception as exc:
            raise RuntimeError("LLM report generation failed with Ollama.") from exc

    # auto: ollama 우선, 실패 시 openai
    try:
        return _try_ollama(prompt=prompt, model=model, base_url=ollama_base_url, timeout_sec=ollama_timeout_sec)
    except Exception:
        pass

    try:
        if not api_key:
            raise RuntimeError("Neither Ollama nor OpenAI is available. Set provider=ollama or provide OPENAI_API_KEY.")
        return _try_openai(prompt=prompt, model=model, api_key=api_key)
    except Exception as exc:
        raise RuntimeError("LLM report generation failed in auto mode.") from exc
