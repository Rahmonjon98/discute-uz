# 🗣️ Discute UZ

Ingliz tilida **gapirishni** mashq qilish dasturi. Siz mikrofonga inglizcha gapirasiz —
AI sizga javob qaytaradi, xatolaringizni **o'zbek tilida** tushuntiradi va javobini
ovozda o'qib beradi.

[Discute](https://github.com/5uru/Discute) loyihasidan ilhomlanib yaratilgan.

## Imkoniyatlar

- 🎙️ **Ovozli suhbat** — mikrofonga gapiring, Whisper (Groq) matnga o'giradi
- 🤖 **Suhbat simulyatsiyasi** — restoran, aeroport, ish suhbati va boshqa ssenariylar
- 🔍 **Xatolar tahlili** — grammatika va so'z tanlash xatolari o'zbekcha izoh bilan
- 🔊 **Ovozli javob** — AI javobini tabiiy ovozda eshitasiz (edge-tts)
- 📊 **Statistika** — suhbatlar tarixi va xatolaringiz tahlili (SQLite)
- 🎚️ **3 daraja** — Beginner / Intermediate / Advanced

## O'rnatish

1. **Python 3.10+** o'rnatilgan bo'lishi kerak.

2. Kutubxonalarni o'rnating:

   ```
   pip install -r requirements.txt
   ```

3. **Groq API kalitini** oling (bepul, karta talab qilinmaydi):
   - [console.groq.com](https://console.groq.com) da ro'yxatdan o'ting
   - [console.groq.com/keys](https://console.groq.com/keys) sahifasida "Create API Key" tugmasini bosing
   - Kalitni nusxalab oling (`gsk_...` bilan boshlanadi)

## Ishga tushirish

```
streamlit run app.py
```

Brauzerda ochilgan sahifada:

1. Chap panelga Groq API kalitingizni kiriting
2. Darajangiz va ssenariyni tanlang
3. "🚀 Suhbatni boshlash" tugmasini bosing
4. Mikrofon belgisini bosib, inglizcha gapiring!

> Maslahat: API kalitini har safar kiritmaslik uchun uni `GROQ_API_KEY`
> muhit o'zgaruvchisiga saqlab qo'yishingiz mumkin.

## Texnologiyalar

| Vazifa | Texnologiya |
|---|---|
| Interfeys | Streamlit |
| Ovoz → matn | Whisper Large V3 Turbo (Groq API) |
| Suhbat va xato tahlili | Llama 3.3 70B (Groq API) |
| Matn → ovoz | edge-tts (zaxira: gTTS) |
| Ma'lumotlar bazasi | SQLite |
