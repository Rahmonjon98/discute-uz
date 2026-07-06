"""Discute UZ — ingliz tilida gapirishni mashq qilish dasturi.

Ishga tushirish:  streamlit run app.py
"""

import os

import streamlit as st
import streamlit.components.v1 as components
from groq import AuthenticationError, RateLimitError

from src import database, tts
from src.config import CHAT_MODELS, LEVELS, VOICES
from src.groq_client import (
    chat_turn,
    generate_random_scenario,
    get_client,
    transcribe_audio,
)
from src.prompts import OPENING_USER_MESSAGE, build_system_prompt
from src.scenarios import CUSTOM_OPTION, RANDOM_OPTION, SCENARIOS

st.set_page_config(page_title="Discute UZ", page_icon="🗣️", layout="centered")

database.init_db()

# ---------------------------------------------------------------- session
DEFAULTS = {
    "messages": [],            # [{role, content, corrected, explanation, tip, has_errors, audio}]
    "conversation_id": None,
    "scenario_title": None,
    "system_prompt": None,
    "level": None,
    "audio_key": 0,            # audio_input widgetini tozalash uchun
    "play_next": False,        # oxirgi AI javobini bir marta avtoijro qilish
    "random_scenario": None,   # (title, setup) — 🎲 tugmasi natijasi
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.session_state.scenario_title = None
    st.session_state.system_prompt = None
    st.session_state.level = None
    st.session_state.play_next = False
    st.session_state.random_scenario = None
    st.session_state.audio_key += 1


def show_api_error(error: Exception) -> None:
    if isinstance(error, AuthenticationError):
        st.error(
            "❌ API kaliti noto'g'ri. [console.groq.com/keys](https://console.groq.com/keys) "
            "sahifasidan yangi kalit oling va chap paneldagi maydonga kiriting."
        )
    elif isinstance(error, RateLimitError):
        st.error("⏳ So'rovlar limitiga yetdingiz. Bir necha daqiqa kutib, qayta urinib ko'ring.")
    else:
        st.error(f"Xatolik yuz berdi: {error}")


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🗣️ Discute UZ")
    st.caption("AI bilan ingliz tilida gaplashib o'rganing")

    page = st.radio(
        "Bo'lim",
        ["💬 Suhbat", "📊 Statistika"],
        label_visibility="collapsed",
    )
    st.divider()

    api_key = st.text_input(
        "Groq API kaliti",
        value=os.environ.get("GROQ_API_KEY", ""),
        type="password",
        help="Bepul kalitni https://console.groq.com/keys sahifasidan oling (karta talab qilinmaydi)",
    )
    model_label = st.selectbox("AI modeli", list(CHAT_MODELS))
    chat_model = CHAT_MODELS[model_label]

    voice_label = st.selectbox("AI ovozi", list(VOICES))
    voice = VOICES[voice_label]
    tts_enabled = st.toggle("Javoblarni ovozda eshitish", value=True)

    if st.session_state.conversation_id is not None:
        st.divider()
        if st.button("🔄 Yangi suhbat boshlash", width="stretch"):
            reset_conversation()
            st.rerun()


# ---------------------------------------------------------------- suhbat qadamlari
def start_conversation(scenario_title: str, scenario_setup: str, level_label: str) -> None:
    """Suhbatni ochadi: AI birinchi bo'lib gapiradi."""
    client = get_client(api_key)
    system_prompt = build_system_prompt(scenario_setup, LEVELS[level_label])

    with st.spinner("🤖 AI suhbatni boshlamoqda..."):
        result = chat_turn(
            client,
            chat_model,
            system_prompt,
            [{"role": "user", "content": OPENING_USER_MESSAGE}],
        )
        audio = tts.synthesize(result["reply"], voice) if tts_enabled else None

    conversation_id = database.create_conversation(scenario_title, level_label)
    database.save_message(conversation_id, "assistant", result["reply"])

    st.session_state.conversation_id = conversation_id
    st.session_state.scenario_title = scenario_title
    st.session_state.system_prompt = system_prompt
    st.session_state.level = level_label
    st.session_state.messages = [
        {"role": "assistant", "content": result["reply"], "audio": audio}
    ]
    st.session_state.play_next = True


def process_turn(user_text: str) -> None:
    """Talabaning gapini qayta ishlaydi: AI javobi + xatolar tahlili + ovoz."""
    client = get_client(api_key)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    history.append({"role": "user", "content": user_text})

    with st.spinner("🤖 AI javob yozmoqda..."):
        result = chat_turn(client, chat_model, st.session_state.system_prompt, history)

    audio = None
    if tts_enabled and result["reply"]:
        with st.spinner("🔊 Ovoz tayyorlanmoqda..."):
            audio = tts.synthesize(result["reply"], voice)

    corrected = result["corrected"] if result["has_errors"] else ""
    explanation = result["explanation"] if result["has_errors"] else ""

    # Avval session'ga yozamiz — baza xatosi suhbat qadamini yo'qotmasin
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text,
            "has_errors": result["has_errors"],
            "corrected": corrected,
            "explanation": explanation,
            "tip": result["tip"],
        }
    )
    st.session_state.messages.append(
        {"role": "assistant", "content": result["reply"], "audio": audio}
    )
    st.session_state.play_next = True

    try:
        database.save_message(
            st.session_state.conversation_id, "user", user_text, corrected, explanation
        )
        database.save_message(
            st.session_state.conversation_id, "assistant", result["reply"]
        )
    except Exception:
        st.toast("⚠️ Tarixga saqlashda xatolik bo'ldi — suhbat davom etaveradi.")


# ---------------------------------------------------------------- sahifa: suhbat
def render_setup_screen() -> None:
    st.header("💬 Yangi suhbat")
    st.write(
        "Ssenariy va darajani tanlang — AI shu vaziyatda siz bilan inglizcha "
        "suhbat quradi, har bir gapingizdagi xatolarni o'zbekcha tushuntirib beradi."
    )

    level_label = st.select_slider("Darajangiz", options=list(LEVELS), value=list(LEVELS)[1])

    options = list(SCENARIOS) + [CUSTOM_OPTION, RANDOM_OPTION]
    choice = st.selectbox("Ssenariy", options)

    scenario_title, scenario_setup = None, None

    if choice == CUSTOM_OPTION:
        custom_text = st.text_area(
            "Ssenariyni o'zingiz yozing (o'zbekcha yoki inglizcha)",
            placeholder="Masalan: Men futbol muxlisiman, stadionda yangi tanish bilan o'yin haqida gaplashyapman...",
        )
        if custom_text.strip():
            scenario_title = "✍️ " + custom_text.strip()[:60]
            scenario_setup = (
                "Role-play scenario described by the student (may be written in Uzbek): "
                f"{custom_text.strip()}\n"
                "Play the other character in this situation."
            )
    elif choice == RANDOM_OPTION:
        if st.button("🎲 Ssenariy yaratish"):
            if not api_key:
                st.warning("Avval chap panelda Groq API kalitini kiriting.")
            else:
                try:
                    with st.spinner("Ssenariy o'ylab topilmoqda..."):
                        st.session_state.random_scenario = generate_random_scenario(
                            get_client(api_key), chat_model
                        )
                except Exception as error:
                    show_api_error(error)
        if st.session_state.random_scenario:
            title, setup = st.session_state.random_scenario
            st.info(f"**{title}**\n\n{setup}")
            scenario_title, scenario_setup = title, setup
    else:
        scenario_title, scenario_setup = choice, SCENARIOS[choice]

    st.divider()
    if st.button("🚀 Suhbatni boshlash", type="primary", width="stretch"):
        if not api_key:
            st.warning(
                "Avval chap panelda Groq API kalitini kiriting. Bepul kalit: "
                "[console.groq.com/keys](https://console.groq.com/keys)"
            )
        elif not scenario_setup:
            st.warning("Ssenariyni tanlang yoki yozing.")
        else:
            # st.rerun() RerunException tashlaydi — uni try ichiga qo'yib bo'lmaydi
            started = False
            try:
                start_conversation(scenario_title, scenario_setup, level_label)
                started = True
            except Exception as error:
                show_api_error(error)
            if started:
                st.rerun()


def render_chat_screen() -> None:
    st.subheader(st.session_state.scenario_title)
    st.caption(f"Daraja: {st.session_state.level} · Model: {model_label}")

    messages = st.session_state.messages
    last_index = len(messages) - 1

    for i, message in enumerate(messages):
        avatar = "🧑‍🎓" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

            if message["role"] == "user":
                if message.get("has_errors"):
                    with st.expander("🔍 Xatolar tahlili", expanded=(i == last_index - 1)):
                        st.markdown(f"**To'g'ri varianti:** {message['corrected']}")
                        if message.get("explanation"):
                            st.markdown(f"**Izoh:** {message['explanation']}")
                        if message.get("tip"):
                            st.markdown(f"💡 **Maslahat:** {message['tip']}")
                else:
                    st.caption("✅ Xatosiz!")
                    if message.get("tip"):
                        st.caption(f"💡 {message['tip']}")

            if message["role"] == "assistant" and message.get("audio"):
                autoplay = st.session_state.play_next and i == last_index
                st.audio(message["audio"], format="audio/mp3", autoplay=autoplay)

    st.session_state.play_next = False

    # ------------------------------------------------------------ kiritish
    audio_recording = st.audio_input(
        "🎙️ Inglizcha gapiring (mikrofon belgisini bosib yozib oling)",
        key=f"audio_input_{st.session_state.audio_key}",
    )
    typed_text = st.chat_input("Yoki javobingizni shu yerga yozing...")

    # Telefonda brauzer autoplay'ni kechiktirib, mikrofon bosilganda AI ovozini
    # qayta ijro qiladi va u yozuvga tushib qoladi. Yechim: mikrofon vidjetiga
    # har tegilganda sahifadagi barcha audio to'xtatiladi (3 soniya davomida
    # qayta urinishlar ham bosiladi).
    components.html(
        """<script>
        const doc = window.parent.document;
        if (!doc._discuteAudioGuard) {
            doc._discuteAudioGuard = true;
            const killAudio = () => doc.querySelectorAll('audio').forEach(a => {
                a.removeAttribute('autoplay');
                if (!a.paused) a.pause();
            });
            doc.addEventListener('pointerdown', (e) => {
                if (e.target.closest('[data-testid="stAudioInput"]')) {
                    killAudio();
                    let n = 0;
                    const iv = setInterval(() => {
                        killAudio();
                        if (++n >= 20) clearInterval(iv);
                    }, 150);
                }
            }, true);
        }
        </script>""",
        height=0,
    )

    # Muvaffaqiyatda rerun qilamiz; xatolikda esa qilmaymiz — aks holda
    # st.error xabari yangi ishga tushirishda yo'qolib ketadi
    if typed_text and typed_text.strip():
        processed = False
        try:
            process_turn(typed_text.strip())
            processed = True
        except Exception as error:
            show_api_error(error)
        if processed:
            st.rerun()

    elif audio_recording is not None:
        st.session_state.audio_key += 1  # widgetni tozalash (qayta ishlanmasin)
        processed = False
        try:
            client = get_client(api_key)
            with st.spinner("🎧 Ovozingiz matnga o'girilmoqda..."):
                text = transcribe_audio(client, audio_recording.read())
            if text:
                process_turn(text)
                processed = True
            else:
                st.warning("Ovoz aniqlanmadi — mikrofonni tekshirib, qayta gapirib ko'ring.")
        except Exception as error:
            show_api_error(error)
        if processed:
            st.rerun()


# ---------------------------------------------------------------- sahifa: statistika
def render_stats_page() -> None:
    st.header("📊 Statistika")
    stats = database.get_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Suhbatlar", stats["conversations"])
    col2.metric("Gaplaringiz", stats["user_messages"])
    col3.metric("Xatolar", stats["mistakes"])
    col4.metric("To'g'rilik", f"{stats['accuracy']}%")

    st.divider()
    st.subheader("So'nggi xatolar tahlili")
    mistakes = database.get_recent_mistakes(20)
    if not mistakes:
        st.info("Hozircha xatolar yo'q. Suhbatni boshlang — natijalar shu yerda ko'rinadi!")
        return

    for m in mistakes:
        with st.expander(f"❌ {m['content'][:80]}"):
            st.markdown(f"**Siz aytdingiz:** {m['content']}")
            st.markdown(f"**To'g'ri varianti:** {m['corrected']}")
            if m["explanation"]:
                st.markdown(f"**Izoh:** {m['explanation']}")
            st.caption(f"{m['scenario']} · {m['created_at']}")


# ---------------------------------------------------------------- routing
if page == "📊 Statistika":
    render_stats_page()
elif st.session_state.conversation_id is None:
    render_setup_screen()
else:
    render_chat_screen()
