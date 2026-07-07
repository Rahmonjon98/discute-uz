"""Dastur sozlamalari: tillar, modellar, ovozlar, darajalar."""

from pathlib import Path

# Loyiha ildizi (src/ papkasining otasi)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Suhbatlar tarixi saqlanadigan SQLite fayl
DB_PATH = PROJECT_ROOT / "discute.db"

# Ovozni matnga o'girish modeli (barcha tillar uchun bitta)
WHISPER_MODEL = "whisper-large-v3-turbo"

# O'rganiladigan tillar: yorliq -> til kodi
LANGUAGES = {
    "🇬🇧 Ingliz tili": "en",
    "🇷🇺 Rus tili": "ru",
}

# Til kodi -> yorliq (statistika sahifasida ko'rsatish uchun)
LANGUAGE_LABELS = {code: label for label, code in LANGUAGES.items()}

# Har bir til uchun sozlamalar. chat_models ro'yxatida birinchi model —
# shu til uchun tavsiya etilgani (selectbox'da avtomatik tanlanadi).
LANGUAGE_CONFIG = {
    "en": {
        "name_uz": "ingliz",   # UI matnlari uchun: "ingliz" + "cha" = "inglizcha"
        "name_en": "English",  # promptlar uchun
        "chat_models": {
            "Llama 3.3 70B (tavsiya etiladi)": "llama-3.3-70b-versatile",
            "GPT-OSS 120B": "openai/gpt-oss-120b",
            "Llama 3.1 8B (eng tez)": "llama-3.1-8b-instant",
        },
        "voices": {
            "Jenny — AQSH, ayol": "en-US-JennyNeural",
            "Guy — AQSH, erkak": "en-US-GuyNeural",
            "Sonia — Britaniya, ayol": "en-GB-SoniaNeural",
            "Ryan — Britaniya, erkak": "en-GB-RyanNeural",
            "Natasha — Avstraliya, ayol": "en-AU-NatashaNeural",
        },
        "grammar_focus": "grammar, word choice, word order, and unnatural phrasing",
    },
    "ru": {
        "name_uz": "rus",
        "name_en": "Russian",
        # Rus tilida GPT-OSS 120B aniqroq ishlaydi: Llama 3.3 rus tilini
        # rasmiy qo'llab-quvvatlamaydi (izohlari g'alizroq chiqadi)
        "chat_models": {
            "GPT-OSS 120B (tavsiya etiladi)": "openai/gpt-oss-120b",
            "Llama 3.3 70B": "llama-3.3-70b-versatile",
            "Llama 3.1 8B (eng tez)": "llama-3.1-8b-instant",
        },
        "voices": {
            "Svetlana — ayol": "ru-RU-SvetlanaNeural",
            "Dmitry — erkak": "ru-RU-DmitryNeural",
        },
        "grammar_focus": (
            "grammar (cases, gender agreement, verb aspect and conjugation), "
            "word choice, and word order"
        ),
    },
}

# Til darajalari va ularga mos AI ko'rsatmalari (barcha tillar uchun umumiy)
LEVELS = {
    "Boshlang'ich (Beginner)": (
        "The student is a BEGINNER (A1-A2). Use very simple, common vocabulary "
        "and short sentences. Avoid idioms. Ask simple questions."
    ),
    "O'rta (Intermediate)": (
        "The student is INTERMEDIATE (B1-B2). Use everyday vocabulary at a natural "
        "pace, with occasional common idioms. Encourage longer answers."
    ),
    "Yuqori (Advanced)": (
        "The student is ADVANCED (C1-C2). Use rich vocabulary, idioms and complex "
        "structures. Challenge the student with follow-up questions and nuance."
    ),
}
