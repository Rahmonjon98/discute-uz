"""Matnni ovozga o'girish: edge-tts (asosiy) + gTTS (zaxira)."""

import asyncio
import io


async def _edge_synthesize(text: str, voice: str) -> bytes:
    import edge_tts

    buffer = bytearray()
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.extend(chunk["data"])
    if not buffer:
        raise RuntimeError("edge-tts bo'sh audio qaytardi")
    return bytes(buffer)


def _gtts_synthesize(text: str) -> bytes | None:
    try:
        from gtts import gTTS

        fp = io.BytesIO()
        gTTS(text=text, lang="en").write_to_fp(fp)
        return fp.getvalue()
    except Exception:
        return None


def synthesize(text: str, voice: str) -> bytes | None:
    """Inglizcha matndan MP3 audio yaratadi.

    Avval edge-tts, ishlamasa gTTS; ikkalasi ham ishlamasa None —
    dastur ovozsiz, faqat matn bilan davom etadi.
    """
    text = (text or "").strip()
    if not text:
        return None
    try:
        return asyncio.run(_edge_synthesize(text, voice))
    except Exception:
        return _gtts_synthesize(text)
