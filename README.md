# 🗣️ Discute UZ

Chet tilida **gapirishni** mashq qilish dasturi (🇬🇧 ingliz va 🇷🇺 rus tillari).
Siz mikrofonga gapirasiz — AI sizga javob qaytaradi, xatolaringizni **o'zbek
tilida** tushuntiradi va javobini ovozda o'qib beradi.

[Discute](https://github.com/5uru/Discute) loyihasidan ilhomlanib yaratilgan.

## Imkoniyatlar

- 🌍 **Ikki til** — ingliz yoki rus tilini tanlang; modellar, ovozlar va
  interfeys avtomatik moslashadi
- 🎙️ **Ovozli suhbat** — mikrofonga gapiring, Whisper (Groq) matnga o'giradi
- 🤖 **Suhbat simulyatsiyasi** — restoran, aeroport, ish suhbati va boshqa ssenariylar
- 🔍 **Xatolar tahlili** — grammatika va so'z tanlash xatolari o'zbekcha izoh bilan
  (rus tilida kelishiklar, rod va fe'l turlari ham)
- 🔊 **Ovozli javob** — AI javobini tabiiy ovozda eshitasiz (edge-tts)
- 📊 **Statistika** — suhbatlar tarixi va xatolaringiz tahlili, til belgisi bilan (SQLite)
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

1. Chap panelda o'rganiladigan tilni tanlang va Groq API kalitingizni kiriting
2. Darajangiz va ssenariyni tanlang
3. "🚀 Suhbatni boshlash" tugmasini bosing
4. Mikrofon belgisini bosib, tanlangan tilda gapiring!

> Maslahat: API kalitini har safar kiritmaslik uchun uni `GROQ_API_KEY`
> muhit o'zgaruvchisiga saqlab qo'yishingiz mumkin.

## Telefonda ishlatish (Streamlit Community Cloud)

1. [share.streamlit.io](https://share.streamlit.io) ga GitHub akkauntingiz bilan kiring
2. **Create app** → repository: `Rahmonjon98/discute-uz`, branch: `master`, main file: `app.py`
3. **Advanced settings → Secrets** maydoniga API kalitingizni kiriting:

   ```toml
   GROQ_API_KEY = "gsk_..."
   ```

4. **Deploy** tugmasini bosing — bir necha daqiqada `https://...streamlit.app` manzili tayyor bo'ladi

> Eslatma: serverda SQLite vaqtinchalik saqlanadi — dastur qayta ishga tushganda
> statistika tarixi tozalanadi. Suhbatning o'ziga bu ta'sir qilmaydi.

## Texnologiyalar

| Vazifa | Texnologiya |
|---|---|
| Interfeys | Streamlit |
| Ovoz → matn | Whisper Large V3 Turbo (Groq API) |
| Suhbat va xato tahlili | Llama 3.3 70B — ingliz, GPT-OSS 120B — rus (Groq API) |
| Matn → ovoz | edge-tts (zaxira: gTTS) |
| Ma'lumotlar bazasi | SQLite |
