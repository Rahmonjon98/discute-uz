"""Dastur sozlamalari: modellar, ovozlar, darajalar."""

from pathlib import Path

# Loyiha ildizi (src/ papkasining otasi)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Suhbatlar tarixi saqlanadigan SQLite fayl
DB_PATH = PROJECT_ROOT / "discute.db"

# Groq'dagi suhbat modellari (2026-yil iyul holatiga ko'ra production modellar)
CHAT_MODELS = {
    "Llama 3.3 70B (tavsiya etiladi)": "llama-3.3-70b-versatile",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "Llama 3.1 8B (eng tez)": "llama-3.1-8b-instant",
}

# Ovozni matnga o'girish modeli
WHISPER_MODEL = "whisper-large-v3-turbo"

# edge-tts ovozlari (ingliz tili)
VOICES = {
    "Jenny — AQSH, ayol": "en-US-JennyNeural",
    "Guy — AQSH, erkak": "en-US-GuyNeural",
    "Sonia — Britaniya, ayol": "en-GB-SoniaNeural",
    "Ryan — Britaniya, erkak": "en-GB-RyanNeural",
    "Natasha — Avstraliya, ayol": "en-AU-NatashaNeural",
}

# Til darajalari va ularga mos AI ko'rsatmalari
LEVELS = {
    "Boshlang'ich (Beginner)": (
        "The student is a BEGINNER (A1-A2). Use very simple, common vocabulary "
        "and short sentences. Avoid idioms and phrasal verbs. Ask simple questions."
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
