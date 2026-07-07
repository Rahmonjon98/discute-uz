"""Groq API bilan ishlash: ovozni matnga o'girish va suhbat."""

import json

from groq import Groq

from src.config import WHISPER_MODEL
from src.prompts import RANDOM_SCENARIO_USER, build_random_scenario_system


def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def transcribe_audio(
    client: Groq,
    audio_bytes: bytes,
    language: str = "en",
    filename: str = "audio.wav",
) -> str:
    """Ovoz yozuvini Whisper orqali tanlangan tildagi matnga o'giradi."""
    result = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=WHISPER_MODEL,
        language=language,
        response_format="text",
    )
    # response_format="text" bo'lsa SDK oddiy str qaytaradi,
    # ba'zi versiyalarda esa .text maydonli obyekt
    text = result if isinstance(result, str) else getattr(result, "text", "")
    return text.strip()


def _mostly_cyrillic(text: str) -> bool:
    """Matn asosan kirill harflaridan iboratmi (izoh ruscha yozilib qolganmi)."""
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    cyrillic = sum(1 for ch in letters if "Ѐ" <= ch <= "ӿ")
    return cyrillic / len(letters) > 0.5


def _pick_uzbek(original: str, retried: str) -> str:
    """Izoh/maslahat uchun yaxshiroq variantni tanlaydi.

    Asl matn o'zbekcha bo'lsa — tegilmaydi; ruscha bo'lsa va retry o'zbekcha
    variant bergan bo'lsa — retry olinadi; retry ham yordam bermasa, hech
    bo'lmaganda borini qoldiramiz.
    """
    if not _mostly_cyrillic(original):
        return original
    if retried and not _mostly_cyrillic(retried):
        return retried
    return original


def _parse_turn(raw: str) -> dict:
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


def chat_turn(client: Groq, model: str, system_prompt: str, history: list[dict]) -> dict:
    """Bitta suhbat qadami: javob + xatolar tahlili (JSON).

    history — [{"role": "user"/"assistant", "content": "..."}] ro'yxati,
    oxirgi element talabaning yangi gapi bo'lishi kerak.
    """

    def request(messages: list[dict]) -> tuple[dict, str]:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        return _parse_turn(raw), raw

    messages = [{"role": "system", "content": system_prompt}] + history
    result, raw = request(messages)

    # Rus tili rejimida model izoh/maslahatni ba'zan ruscha yozib qo'yadi —
    # bunday holda bir marta o'zbekchaga qayta yozishni so'raymiz
    if _mostly_cyrillic(result["explanation"]) or _mostly_cyrillic(result["tip"]):
        retry_messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "(SYSTEM CHECK: your explanation/tip were not in Uzbek. Return "
                    "the SAME JSON again, keeping reply and corrected unchanged, but "
                    "rewrite explanation and tip in UZBEK latin script.)"
                ),
            },
        ]
        try:
            retried, _ = request(retry_messages)
        except Exception:
            # Retry muvaffaqiyatsiz bo'lsa (masalan, limit) — asl javob
            # bilan davom etamiz, tayyor suhbat qadami yo'qolmasin
            retried = None
        if retried:
            # reply/corrected asl javobdan olinadi — suhbat oqimi o'zgarmasin;
            # izoh va maslahat esa alohida-alohida baholanadi
            result["explanation"] = _pick_uzbek(result["explanation"], retried["explanation"])
            result["tip"] = _pick_uzbek(result["tip"], retried["tip"])

    return result


def generate_random_scenario(client: Groq, model: str, language_name: str) -> tuple[str, str]:
    """Tanlangan til uchun tasodifiy ssenariy yaratadi: (o'zbekcha nom, inglizcha tavsif)."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_random_scenario_system(language_name)},
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
