"""Groq API bilan ishlash: ovozni matnga o'girish va suhbat."""

import json

from groq import Groq

from src.config import WHISPER_MODEL
from src.prompts import RANDOM_SCENARIO_SYSTEM, RANDOM_SCENARIO_USER


def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def transcribe_audio(client: Groq, audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Ovoz yozuvini Whisper orqali inglizcha matnga o'giradi."""
    result = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=WHISPER_MODEL,
        language="en",
        response_format="text",
    )
    # response_format="text" bo'lsa SDK oddiy str qaytaradi,
    # ba'zi versiyalarda esa .text maydonli obyekt
    text = result if isinstance(result, str) else getattr(result, "text", "")
    return text.strip()


def chat_turn(client: Groq, model: str, system_prompt: str, history: list[dict]) -> dict:
    """Bitta suhbat qadami: javob + xatolar tahlili (JSON).

    history — [{"role": "user"/"assistant", "content": "..."}] ro'yxati,
    oxirgi element talabaning yangi gapi bo'lishi kerak.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0.7,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # JSON buzilgan bo'lsa — javobni oddiy matn sifatida qabul qilamiz
        data = {"reply": raw}

    corrected = str(data.get("corrected") or "").strip()
    return {
        "reply": str(data.get("reply") or "").strip(),
        # Model ba'zan has_errors=true deb, corrected'ni bo'sh qoldiradi —
        # UI va statistika mos bo'lishi uchun ikkalasini birga talab qilamiz
        "has_errors": bool(data.get("has_errors", False)) and bool(corrected),
        "corrected": corrected,
        "explanation": str(data.get("explanation") or "").strip(),
        "tip": str(data.get("tip") or "").strip(),
    }


def generate_random_scenario(client: Groq, model: str) -> tuple[str, str]:
    """Tasodifiy ssenariy yaratadi: (o'zbekcha nom, inglizcha tavsif)."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": RANDOM_SCENARIO_SYSTEM},
            {"role": "user", "content": RANDOM_SCENARIO_USER},
        ],
        temperature=1.0,
        max_tokens=400,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content or "{}")
    title = str(data.get("title_uz") or "🎲 Tasodifiy ssenariy").strip()
    setup = str(data.get("setup") or "").strip()
    if not setup:
        raise ValueError("Ssenariy yaratilmadi, qayta urinib ko'ring.")
    return title, setup
