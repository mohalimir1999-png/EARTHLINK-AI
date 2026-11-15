
import streamlit as st
import io
import numpy as np
from pathlib import Path
from scipy.io import wavfile
st.set_page_config(
    page_title="EARTHLINK-AI",
    page_icon="🌍",
    layout="wide"
)
def make_real_instruments_music(beat_times, instrument="Fusion", sample_rate=22050):
    from scipy.signal import resample_poly
    from math import gcd

    duration = 30.0
    total = int(duration * sample_rate)
    audio = np.zeros(total, dtype=np.float64)

    sample_dir = Path(__file__).resolve().parent / "music_samples"

    
    harp_specs = [
        ("373556_", 0.20),
        ("373563_", 0.22),
        ("373565_", 0.20),
        ("373568_", 0.20),
    ]

    handpan_specs = [
        ("587401_", 0.14),
        ("587412_", 0.14),
        ("587414_", 0.14),
        ("587415_", 0.14),
        ("587418_", 0.14),
        ("692829_", 0.12),
    ]

    if instrument == "Harp":
        sample_specs = harp_specs
    elif instrument == "Handpan":
        sample_specs = handpan_specs
    else:
        sample_specs = harp_specs + handpan_specs


    samples = []

    for prefix, volume in sample_specs:
        matches = sorted(sample_dir.glob(prefix + "*.wav"))

        if not matches:
            raise FileNotFoundError(
                f"Missing WAV sample beginning with {prefix}"
            )

        fs, sound = wavfile.read(str(matches[0]))
        sound = np.asarray(sound, dtype=np.float64)

        if sound.ndim == 2:
            sound = sound.mean(axis=1)

        peak = np.max(np.abs(sound))
        if peak > 0:
            sound = sound / peak

        divisor = gcd(int(fs), sample_rate)
        sound = resample_poly(
            sound,
            sample_rate // divisor,
            int(fs) // divisor
        )

        peak = np.max(np.abs(sound))
        if peak > 0:
            sound = sound / peak

        samples.append((sound, volume))

    for i, beat_time in enumerate(beat_times):
        start = int(float(beat_time) * sample_rate)

        if start < 0 or start >= total:
            continue

        # Play real instrument samples at ECG heartbeat times.
        sound, volume = samples[i % len(samples)]

        length = min(len(sound), total - start)
        if length <= 0:
            continue

        audio[start:start + length] += volume * sound[:length]

    # Smooth beginning and ending.
    fade = int(0.5 * sample_rate)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.85

    pcm = (audio * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm)

    return buffer.getvalue()
st.title("🌍 EARTHLINK-AI")
st.subheader("Astronaut Health Monitoring & Emotional Support System")

st.success("System initialized successfully!")

st.divider()

st.header("👨‍🚀 Astronaut Health Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Heart Rate", "72 bpm")

with col2:
    st.metric("Stress Level", "Low")

with col3:
    st.metric("Sleep Duration", "7.5 hours")

st.divider()

st.header("❤️ Emotional Connection to Earth")

st.write(
    "Personalized emotional support for astronauts "
    "during long-duration space missions."
)

if st.button("Connect to Earth 🌍"):
    st.success("Emotional connection activated!")
    st.write("A familiar voice. A precious memory. A connection to home.")

st.caption("EARTHLINK-AI | NASA Space Apps Challenge 2026")

st.divider()

st.header("🩺 Astronaut Health Assessment")

st.write("Enter your current health information.")

heart_rate = st.number_input(
    "Heart Rate (bpm)",
    min_value=40,
    max_value=180,
    value=72
)

stress = st.slider(
    "How stressed do you feel? (0-10)",
    min_value=0,
    max_value=10,
    value=5
)

sleep = st.slider(
    "Sleep Duration (hours)",
    min_value=0.0,
    max_value=12.0,
    value=7.0,
    step=0.5
)

if st.button("Analyze My Health"):
    st.subheader("Health Assessment Results")

    if stress >= 7:
        st.warning("High self-reported stress. Consider a supportive activity.")
    else:
        st.success("Self-reported stress is below the demo alert threshold.")

    if sleep < 6:
        st.warning("Short sleep duration reported.")
    else:
        st.info("Sleep duration recorded.")

    if heart_rate > 100:
        st.warning("Heart rate exceeds the demo alert threshold.")
    else:
        st.info("Heart rate recorded.")

    st.caption(
        "Prototype only. These thresholds are illustrative "
        "and are not validated for astronaut medical assessment."
    )

# ==========================================
# EARTHLINK-AI - Health History & Trends
# ==========================================

import pandas as pd
from pathlib import Path
from datetime import date

st.divider()
st.header("📊 Astronaut Health History")

st.write(
    "Save daily health measurements and monitor "
    "changes during the space mission."
)

data_file = Path("health_history.csv")

# Load saved measurements
if data_file.exists():
    history = pd.read_csv(data_file)
else:
    history = pd.DataFrame(
        columns=["Date", "Heart Rate", "Stress", "Sleep"]
    )

measurement_date = st.date_input(
    "Measurement Date",
    value=date.today()
)

if st.button("💾 Save Health Record"):
    new_record = pd.DataFrame([{
        "Date": str(measurement_date),
        "Heart Rate": heart_rate,
        "Stress": stress,
        "Sleep": sleep
    }])

    history = pd.concat(
        [history, new_record],
        ignore_index=True
    )

    history.to_csv(data_file, index=False)

    st.success("Health record saved successfully!")

# Reload saved records
if data_file.exists():
    history = pd.read_csv(data_file)

if not history.empty:
    st.subheader("📋 Recorded Health Data")

    st.dataframe(
        history,
        use_container_width=True
    )

    st.subheader("📈 Health Trends")

    history["Date"] = pd.to_datetime(history["Date"])
    history = history.sort_values("Date")

    st.write("Heart Rate Trend")
    st.line_chart(
        history.set_index("Date")["Heart Rate"]
    )

    st.write("Stress Level Trend")
    st.line_chart(
        history.set_index("Date")["Stress"]
    )

    st.write("Sleep Duration Trend")
    st.line_chart(
        history.set_index("Date")["Sleep"]
    )
else:
    st.info("No health records saved yet.")

st.caption(
    "Prototype monitoring tool. Data are entered manually "
    "and do not represent validated medical measurements."
)

# EARTHLINK-AI - Personalized Emotional Support

st.divider()
st.header("🌍 Personalized Emotional Support")

st.write(
    "Receive supportive recommendations based on "
    "your current health and emotional state."
)

emotional_stress = st.slider(
    "Current stress level (1-10)",
    min_value=1,
    max_value=10,
    value=5,
    key="emotional_stress"
)

emotional_sleep = st.number_input(
    "Sleep during the last 24 hours (hours)",
    min_value=0.0,
    max_value=24.0,
    value=7.0,
    step=0.5,
    key="emotional_sleep"
)

connection_level = st.slider(
    "How connected do you feel to Earth? (1-10)",
    min_value=1,
    max_value=10,
    value=5,
    key="connection_level"
)

if st.button("💙 Generate My Support Plan"):

    st.subheader("Your Personalized Support Plan")

    if emotional_stress >= 7:
        st.warning("High self-reported stress detected.")
        st.write(
            "🎧 Consider listening to a familiar voice "
            "or a positive recorded message from a loved one."
        )

    if emotional_sleep < 6:
        st.info("Short sleep duration reported.")
        st.write(
            "🌙 Consider a calming audio experience "
            "and reviewing your rest schedule."
        )

    if connection_level <= 4:
        st.write(
            "🌍 Earth Connection Recommendation: "
            "Explore a meaningful photo, familiar sound, "
            "or positive memory from home."
        )

    if (
        emotional_stress < 7
        and emotional_sleep >= 6
        and connection_level > 4
    ):
        st.success(
            "No support triggers identified by "
            "the current demonstration rules."
        )
        st.write(
            "💚 You can still enjoy a positive "
            "memory or familiar message."
        )

    st.caption(
        "Prototype only. Recommendations are supportive, "
        "not medical diagnoses or validated treatments."
    )
# ==========================================
# EARTHLINK-AI
# Maternal Heartbeat-Derived Music
# ==========================================

import numpy as np
import io
import wave

st.divider()

st.header("🎼 Maternal Heartbeat-Derived Music")

st.write(
    "Experience a personalized musical composition "
    "inspired by the rhythm of a mother's heartbeat."
)

st.info(
    "This prototype uses simulated heartbeat intervals. "
    "It does not use a real maternal ECG recording."
)

mother_hr = st.slider(
    "Simulated Maternal Heart Rate (bpm)",
    min_value=55,
    max_value=100,
    value=72,
    key="mother_hr"
)

heartbeat_influence = st.slider(
    "Heartbeat Rhythm Influence (%)",
    min_value=0,
    max_value=100,
    value=60,
    key="heartbeat_influence"
)

music_duration = st.slider(
    "Music Duration (seconds)",
    min_value=10,
    max_value=60,
    value=20,
    step=5,
    key="music_duration"
)


def generate_heartbeat_music(
    heart_rate,
    influence,
    duration
):
    sample_rate = 22050

    total_samples = int(duration * sample_rate)

    time = np.arange(total_samples) / sample_rate

    # Musical notes in a calming pentatonic scale
    notes = [
        261.63,
        293.66,
        329.63,
        392.00,
        440.00
    ]

    music = np.zeros(total_samples)

    beat_interval = 60.0 / heart_rate

    rng = np.random.default_rng(42)

    current_time = 0.0
    note_index = 0

    while current_time < duration:

        # Simulated natural variation between beats
        variation = rng.normal(0, 0.035)

        interval = max(
            0.4,
            beat_interval + variation
        )

        # Blend heartbeat timing with a steady rhythm
        steady_interval = 0.8

        blended_interval = (
            (influence / 100) * interval
            + (1 - influence / 100) * steady_interval
        )

        start = int(current_time * sample_rate)

        note_duration = min(
            0.7,
            blended_interval * 0.9
        )

        length = int(note_duration * sample_rate)

        end = min(start + length, total_samples)

        actual_length = end - start

        if actual_length <= 0:
            break

        local_time = (
            np.arange(actual_length) / sample_rate
        )

        frequency = notes[note_index % len(notes)]

        # Soft musical tone with harmonics
        tone = (
            np.sin(2 * np.pi * frequency * local_time)
            + 0.25 * np.sin(
                2 * np.pi * frequency * 2 * local_time
            )
        )

        # Smooth fade-in and fade-out
        envelope = np.sin(
            np.pi * np.linspace(
                0,
                1,
                actual_length
            )
        ) ** 2

        music[start:end] += (
            0.22 * tone * envelope
        )

        current_time += blended_interval

        note_index += 1

    # Soft harmonic background
    background = (
        0.07 * np.sin(2 * np.pi * 130.81 * time)
        + 0.05 * np.sin(2 * np.pi * 196.00 * time)
    )

    # Fade the beginning and end
    fade = np.ones(total_samples)
    fade_samples = min(sample_rate, total_samples // 2)

    fade[:fade_samples] = np.linspace(
        0, 1, fade_samples
    )

    fade[-fade_samples:] = np.linspace(
        1, 0, fade_samples
    )

    audio = (music + background) * fade

    peak = np.max(np.abs(audio))

    if peak > 0:
        audio = audio / peak * 0.75

    audio_int16 = (
        audio * 32767
    ).astype(np.int16)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())

    buffer.seek(0)

    return buffer.getvalue()


if st.button("🎵 Generate Heartbeat Music"):

    with st.spinner("Composing your personalized music..."):

        audio_data = generate_heartbeat_music(
            mother_hr,
            heartbeat_influence,
            music_duration
        )

    st.session_state["heartbeat_music"] = audio_data

    st.success("Your personalized music is ready!")


if "heartbeat_music" in st.session_state:

    st.audio(
        st.session_state["heartbeat_music"],
        format="audio/wav"
    )

    st.download_button(
        "⬇️ Download Personalized Music",
        data=st.session_state["heartbeat_music"],
        file_name="EARTHLINK_AI_Heartbeat_Music.wav",
        mime="audio/wav"
    )

st.caption(
    "Experimental sonification prototype. "
    "No therapeutic effectiveness is claimed."
)


# ==========================================
# EARTHLINK-AI - Earth Heartbeat Connection
# Music + Warm Light + Loved One Photo
# ==========================================

import io
import wave
import base64
import json
import numpy as np
import streamlit.components.v1 as components

st.divider()
st.header("❤️ Earth Heartbeat Connection")
st.subheader("Maternal Heartbeat Memory Mode")

st.write(
    "A personal memory experience combining music, "
    "a loved one's photo, and synchronized warm light."
)

person_name = st.text_input(
    "Name of your loved one (optional)",
    placeholder="Someone special",
    key="memory_person_name"
)

memory_photo = st.file_uploader(
    "Upload a photo of your loved one",
    type=["jpg", "jpeg", "png"],
    key="memory_photo_upload"
)

memory_rate = st.slider(
    "Simulated Heart Rate (bpm)",
    min_value=55,
    max_value=100,
    value=72,
    key="memory_heart_rate"
)

memory_seconds = st.select_slider(
    "Experience Duration (seconds)",
    options=[20, 30, 45, 60],
    value=30,
    key="memory_seconds"
)


def build_earth_memory(hr, duration):
    sr = 22050
    count = int(sr * duration)
    audio = np.zeros(count, dtype=np.float64)
    rng = np.random.default_rng(2026)

    # One simulated heartbeat pattern controls
    # both the musical timing and the warm light.
    beats = []
    moment = 0.5

    while moment < duration:
        beats.append(round(moment, 4))
        interval = 60.0 / hr
        interval += rng.normal(0, 0.025)
        moment += max(0.45, interval)

    # Warm, evolving ambient harmony
    chords = [
        [130.81, 164.81, 196.00, 261.63],
        [110.00, 164.81, 220.00, 261.63],
        [87.31, 130.81, 174.61, 220.00],
        [98.00, 146.83, 196.00, 246.94]
    ]

    for chord_number, start_time in enumerate(
        range(0, duration, 8)
    ):
        start = int(start_time * sr)
        end = min(count, int((start_time + 8) * sr))
        local = np.arange(end - start) / sr

        envelope = (
            np.minimum(1.0, local / 1.3)
            * np.minimum(1.0, (len(local) / sr - local) / 1.3)
        )
        envelope = np.maximum(0, envelope)

        pad = np.zeros(len(local))

        for frequency in chords[chord_number % 4]:
            pad += (
                np.sin(2 * np.pi * frequency * local)
                + 0.12 * np.sin(4 * np.pi * frequency * local)
            )

        audio[start:end] += 0.018 * pad * envelope

    # Emotional melodic phrases
    melody = [
        392.00, 440.00, 523.25, 440.00,
        392.00, 329.63, 349.23, 392.00,
        440.00, 523.25, 587.33, 523.25,
        440.00, 392.00, 349.23, 329.63
    ]

    for i, beat in enumerate(beats):
        if i % 8 == 7:
            continue

        start = int(beat * sr)
        end = min(count, start + int(1.5 * sr))
        local = np.arange(end - start) / sr

        if len(local) == 0:
            continue

        frequency = melody[i % len(melody)]

        envelope = (
            (1 - np.exp(-30 * local))
            * np.exp(-2.1 * local)
        )

        tone = (
            np.sin(2 * np.pi * frequency * local)
            + 0.20 * np.sin(4 * np.pi * frequency * local)
            + 0.07 * np.sin(6 * np.pi * frequency * local)
        )

        audio[start:end] += 0.12 * tone * envelope

    # Gentle fade in and fade out
    fade_samples = min(sr * 2, count // 2)
    fade = np.ones(count)
    fade[:fade_samples] = np.linspace(0, 1, fade_samples)
    fade[-fade_samples:] = np.linspace(1, 0, fade_samples)

    audio *= fade

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.65

    pcm = (audio * 32767).astype(np.int16)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(pcm.tobytes())

    return buffer.getvalue(), beats


if st.button("✨ Create My Earth Memory", key="create_earth_memory"):
    with st.spinner("Creating your personal experience..."):
        sound, beat_pattern = build_earth_memory(
            memory_rate,
            memory_seconds
        )

    st.session_state["earth_memory_result"] = {
        "sound": sound,
        "beats": beat_pattern
    }

    st.success("Your Earth Memory is ready!")


if "earth_memory_result" in st.session_state:

    result = st.session_state["earth_memory_result"]

    sound64 = base64.b64encode(
        result["sound"]
    ).decode("ascii")

    if memory_photo is not None:
        image64 = base64.b64encode(
            memory_photo.getvalue()
        ).decode("ascii")

        image_type = (
            "image/png"
            if memory_photo.type == "image/png"
            else "image/jpeg"
        )

        photo_source = (
            f"data:{image_type};base64,{image64}"
        )
    else:
        photo_source = ""

    # JSON encoding safely transfers text to JavaScript
    config = json.dumps({
        "beats": result["beats"],
        "photo": photo_source,
        "name": person_name or "A Memory of Home"
    }).replace("<", "\\u003c")

    html = """
    <div class="scene">
      <h2 id="memoryTitle">A Memory of Home</h2>

      <canvas id="lightCanvas" width="600" height="320"></canvas>

      <p>Music and warm light share one heartbeat pattern.</p>

      <audio id="memoryAudio" controls>
        <source src="data:audio/wav;base64,AUDIO_HERE"
                type="audio/wav">
      </audio>

      <p class="hint">
        Press Play to begin. Pause or seek to control the light.
      </p>
    </div>

    <style>
      body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: #101525;
      }
      .scene {
        background: radial-gradient(
          ellipse, #24283c, #101525 75%
        );
        border-radius: 20px;
        padding: 18px;
        color: #f8e6ce;
        text-align: center;
      }
      h2 { font-size: 20px; }
      canvas {
        width: 100%;
        max-width: 600px;
        display: block;
        margin: auto;
      }
      audio {
        width: 95%;
        max-width: 480px;
      }
      p { font-size: 13px; }
      .hint { opacity: 0.7; }
    </style>

    <script>
      const config = CONFIG_HERE;
      const beats = config.beats;
      const audio = document.getElementById("memoryAudio");
      const canvas = document.getElementById("lightCanvas");
      const ctx = canvas.getContext("2d");

      document.getElementById("memoryTitle").textContent =
        config.name;

      const photo = new Image();
      if (config.photo) photo.src = config.photo;

      function animate() {
        const w = canvas.width;
        const h = canvas.height;
        const x = w / 2;
        const y = h / 2;
        const time = audio.currentTime;

        ctx.clearRect(0, 0, w, h);

        let pulse = 0;

        if (!audio.paused && !audio.ended) {
          for (const beat of beats) {
            const dt = time - beat;

            if (dt >= 0 && dt < 0.8) {
              const main = Math.exp(
                -Math.pow((dt - 0.13) / 0.15, 2)
              );
              const echo = 0.25 * Math.exp(
                -Math.pow((dt - 0.36) / 0.13, 2)
              );
              pulse = Math.max(pulse, main + echo);
            }
          }
        }

        const radius = 80 + pulse * 15;
        const brightness = 0.35 + pulse * 0.30;

        const glow = ctx.createRadialGradient(
          x, y, 15, x, y, radius * 2.1
        );

        glow.addColorStop(
          0, "rgba(255,225,160," + brightness + ")"
        );
        glow.addColorStop(
          0.5, "rgba(255,160,100,0.18)"
        );
        glow.addColorStop(
          1, "rgba(255,160,100,0)"
        );

        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(x, y, radius * 2.1, 0, Math.PI * 2);
        ctx.fill();

        if (photo.complete && photo.naturalWidth > 0) {
          const size = 155;

          ctx.save();
          ctx.beginPath();
          ctx.arc(x, y, size / 2, 0, Math.PI * 2);
          ctx.clip();

          const scale = Math.max(
            size / photo.naturalWidth,
            size / photo.naturalHeight
          );

          const pw = photo.naturalWidth * scale;
          const ph = photo.naturalHeight * scale;

          ctx.drawImage(
            photo, x - pw / 2, y - ph / 2, pw, ph
          );

          ctx.restore();

          ctx.beginPath();
          ctx.arc(x, y, size / 2 + 3 + pulse * 5,
                  0, Math.PI * 2);
          ctx.strokeStyle = "rgba(255,213,154,0.65)";
          ctx.lineWidth = 3;
          ctx.stroke();

        } else {
          const core = ctx.createRadialGradient(
            x - 15, y - 15, 3, x, y, radius
          );

          core.addColorStop(0, "#fff4d6");
          core.addColorStop(0.6, "#ffd49c");
          core.addColorStop(1, "#e8a16e");

          ctx.fillStyle = core;
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, Math.PI * 2);
          ctx.fill();
        }

        requestAnimationFrame(animate);
      }

      animate();
    </script>
    """

    html = html.replace(
        "AUDIO_HERE", sound64
    ).replace(
        "CONFIG_HERE", config
    )

    components.html(
        html,
        height=490,
        scrolling=False
    )

    st.download_button(
        "⬇️ Download Memory Music",
        data=result["sound"],
        file_name="EARTHLINK_Earth_Memory.wav",
        mime="audio/wav",
        key="download_earth_memory"
    )

st.caption(
    "Research prototype with simulated heartbeat data. "
    "No therapeutic effectiveness has been established."
)

# ==============================================
# EARTHLINK-AI | Messages & Memories From Earth
# ==============================================

st.divider()
st.header("🌍 Messages & Memories From Earth")

st.write(
    "Reconnect with meaningful people and positive "
    "memories during a long-duration space mission."
)

memory_type = st.selectbox(
    "Choose your memory experience",
    [
        "Voice Message",
        "Video Message",
        "Written Message",
        "Group Memory"
    ],
    key="earth_messages_type"
)

sender_name = st.text_input(
    "Who is this memory from?",
    placeholder="Mom, Dad, My Child, Friends...",
    key="earth_messages_sender"
)

st.caption(
    "Use recordings and images with permission. "
    "Demo uploads are not saved as separate files."
)

# Optional photo for voice and written memories
message_photo = None

if memory_type in ["Voice Message", "Written Message"]:
    message_photo = st.file_uploader(
        "Upload a photo (optional)",
        type=["jpg", "jpeg", "png"],
        key="earth_messages_photo"
    )

# Upload the selected memory
message_audio = None
message_video = None
message_text = ""

if memory_type == "Voice Message":
    message_audio = st.file_uploader(
        "Upload a voice recording",
        type=["mp3", "wav", "m4a"],
        key="earth_messages_audio"
    )

elif memory_type in ["Video Message", "Group Memory"]:
    message_video = st.file_uploader(
        "Upload a family or friends video",
        type=["mp4", "mov", "webm"],
        key="earth_messages_video"
    )

elif memory_type == "Written Message":
    message_text = st.text_area(
        "Write a positive message from home",
        placeholder="We love you and are proud of you...",
        key="earth_messages_text"
    )

# Simple rule-based soundtrack selection
st.subheader("🎵 Adaptive Soundtrack")

if memory_type in ["Video Message", "Group Memory"]:
    st.info(
        "Recommendation: Keep background music off "
        "so voices and shared memories remain clear."
    )
    allow_background = False

elif memory_type == "Voice Message":
    st.info(
        "Recommendation: Prioritize the familiar voice. "
        "Optional heartbeat music can be played quietly."
    )
    allow_background = st.checkbox(
        "Show optional heartbeat background music",
        value=False,
        key="earth_messages_voice_music"
    )

else:
    st.info(
        "Recommendation: Gentle heartbeat-derived music "
        "may accompany a written memory."
    )
    allow_background = st.checkbox(
        "Show heartbeat-derived music",
        value=True,
        key="earth_messages_text_music"
    )

# Show the selected memory
st.divider()
st.subheader("💙 Your Memory From Home")

if sender_name.strip():
    st.write("A message from " + sender_name.strip())

if message_photo is not None:
    st.image(
        message_photo,
        width=320
    )

if memory_type == "Voice Message":
    if message_audio is not None:
        st.audio(message_audio)
    else:
        st.info("Upload a voice message to listen.")

elif memory_type in ["Video Message", "Group Memory"]:
    if message_video is not None:
        st.video(message_video)
    else:
        st.info("Upload a video to watch.")

elif memory_type == "Written Message":
    if message_text.strip():
        st.success(message_text)
    else:
        st.info("Enter a message to display.")

# Reuse music already created in the previous module
if allow_background:
    st.subheader("❤️ Optional Heartbeat Music")

    if "earth_memory_result" in st.session_state:
        st.audio(
            st.session_state["earth_memory_result"]["sound"],
            format="audio/wav"
        )

        st.caption(
            "Optional music player. Start or pause it "
            "manually. Audio mixing and automatic volume "
            "ducking are not implemented yet."
        )
    else:
        st.info(
            "First generate music in the Earth Heartbeat "
            "Connection section above."
        )

st.caption(
    "Prototype: soundtrack recommendations use "
    "simple rules, not a trained AI model. "
    "Emotional or clinical benefits are not established."
)


# ==============================================
# EARTHLINK-AI | Unified Memory Experience
# ==============================================

st.divider()
st.header("🌍 Unified Memory Experience")

st.write(
    "A personal message from Earth, accompanied by "
    "heartbeat-inspired music and synchronized warm light."
)

unified_name = st.text_input(
    "Who is this memory from?",
    value="Mom",
    key="unified_name"
)

unified_photo = st.file_uploader(
    "Choose a photo",
    type=["png", "jpg", "jpeg"],
    key="unified_photo"
)

unified_message = st.text_area(
    "Message from home",
    value=(
        "My dear, wherever you are among the stars, "
        "you are always close to my heart. "
        "We love you and are so proud of you."
    ),
    key="unified_message"
)

unified_hr = st.slider(
    "Simulated Heart Rate (bpm)",
    55, 100, 72,
    key="unified_hr"
)

unified_volume = st.slider(
    "Background Music Volume (%)",
    0, 100, 25,
    key="unified_volume"
)

unified_instrument = st.selectbox(
    "Choose Music for Your Memory",
    ["Fusion", "Harp", "Handpan"],
       key="unified_instrument"
)

if st.button(
    "❤️ Create Unified Memory",
    key="unified_create"
):
    with st.spinner("Preparing your memory..."):
        unified_sound, unified_beats = build_earth_memory(
            unified_hr, 30
        )

        music_choice = (
            "Combined"
            if unified_instrument == "Fusion"
            else unified_instrument
        )

        unified_sound = make_real_instruments_music(
            unified_beats,
            music_choice
        )

        st.session_state["unified_result"] = {
            "sound": unified_sound,
            "beats": unified_beats
        }
unified_audio64 = ""
unified_result = st.session_state.get(
    "unified_result",
    {"sound": b"", "beats": []}
)
if "unified_result" in st.session_state:

    unified_result = st.session_state["unified_result"]

    unified_audio64 = base64.b64encode(
        unified_result["sound"]
    ).decode("ascii")

    
unified_photo_source = ""

default_mom_photo = (
    Path(__file__).resolve().parent
    / "demo_assets"
    / "anastasia_ai.png"
)

if default_mom_photo.is_file():
    default_mom_image64 = base64.b64encode(
        default_mom_photo.read_bytes()
    ).decode("ascii")

    unified_photo_source = (
        f"data:image/png;base64,{default_mom_image64}"
    )


    if unified_photo is not None:
        unified_image64 = base64.b64encode(
            unified_photo.getvalue()
        ).decode("ascii")

        unified_mime = (
            "image/png"
            if unified_photo.type == "image/png"
            else "image/jpeg"
        )

        unified_photo_source = (
            f"data:{unified_mime};base64,{unified_image64}"
        )

    unified_config = json.dumps({
        "name": unified_name,
        "message": unified_message,
        "photo": unified_photo_source,
        "beats": unified_result["beats"],
        "volume": unified_volume / 100
    }).replace("<", "\\u003c")

    unified_html = """
    <div class="memory">
      <h2>A Message From Home</h2>
      <h3 id="personName"></h3>

      <canvas id="scene" width="600" height="310"></canvas>

      <p id="personalMessage"></p>

      <audio id="music" controls>
        <source
          src="data:audio/wav;base64,AUDIO_HERE"
          type="audio/wav">
      </audio>

      <p class="note">
        Press Play to begin the synchronized experience.
      </p>
    </div>

    <style>
      body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: #111525;
      }

      .memory {
        padding: 20px;
        text-align: center;
        background: radial-gradient(
          ellipse, #29253b, #111525 80%
        );
        color: #ffe8d4;
        border-radius: 20px;
      }

      h2 { font-size: 22px; }
      h3 { font-size: 16px; color: #ffcfaa; }

      canvas {
        width: 100%;
        max-width: 600px;
      }

      #personalMessage {
        font-size: 16px;
        line-height: 1.6;
        max-width: 520px;
        margin: 12px auto 20px;
      }

      audio {
        width: 90%;
        max-width: 450px;
      }

      .note {
        font-size: 12px;
        opacity: 0.7;
      }
    </style>

    <script>
      const config = CONFIG_HERE;
      const audio = document.getElementById("music");
      const canvas = document.getElementById("scene");
      const ctx = canvas.getContext("2d");

      audio.volume = config.volume;

      document.getElementById("personName").textContent =
        config.name || "Someone Special";

      document.getElementById("personalMessage").textContent =
        config.message;

      const photo = new Image();
      if (config.photo) photo.src = config.photo;

      function animate() {
        const x = canvas.width / 2;
        const y = canvas.height / 2;
        const time = audio.currentTime;

        ctx.clearRect(
          0, 0, canvas.width, canvas.height
        );

        let pulse = 0;

        if (!audio.paused && !audio.ended) {
          for (const beat of config.beats) {
            const dt = time - beat;

            if (dt >= 0 && dt < 0.8) {
              const main = Math.exp(
                -Math.pow((dt - 0.12) / 0.15, 2)
              );

              const echo = 0.25 * Math.exp(
                -Math.pow((dt - 0.35) / 0.14, 2)
              );

              pulse = Math.max(pulse, main + echo);
            }
          }
        }

        const radius = 88 + pulse * 19;
        const intensity = 0.35 + pulse * 0.35;

        const glow = ctx.createRadialGradient(
          x, y, 5, x, y, radius * 2
        );

        glow.addColorStop(
          0, "rgba(255,230,170," + intensity + ")"
        );
        glow.addColorStop(
          0.5, "rgba(255,170,105,0.22)"
        );
        glow.addColorStop(
          1, "rgba(255,140,90,0)"
        );

        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(x, y, radius * 2, 0, Math.PI * 2);
        ctx.fill();

        if (photo.complete && photo.naturalWidth > 0) {
          const size = 160;

          ctx.save();
          ctx.beginPath();
          ctx.arc(x, y, size / 2, 0, Math.PI * 2);
          ctx.clip();

          const scale = Math.max(
            size / photo.naturalWidth,
            size / photo.naturalHeight
          );

          const pw = photo.naturalWidth * scale;
          const ph = photo.naturalHeight * scale;

          ctx.drawImage(
            photo,
            x - pw / 2,
            y - ph / 2,
            pw,
            ph
          );

          ctx.restore();

          ctx.strokeStyle = "#ffd39a";
          ctx.lineWidth = 3 + pulse * 5;

          ctx.beginPath();
          ctx.arc(
            x, y, size / 2 + 5 + pulse * 4,
            0, Math.PI * 2
          );
          ctx.stroke();

        } else {
          ctx.fillStyle = "#ffd49b";
          ctx.beginPath();
          ctx.arc(x, y, 65 + pulse * 10,
                  0, Math.PI * 2);
          ctx.fill();
        }

        requestAnimationFrame(animate);
      }

      animate();
    </script>
    """

    unified_html = unified_html.replace(
        "AUDIO_HERE", unified_audio64
    ).replace(
        "CONFIG_HERE", unified_config
    )

    components.html(
        unified_html,
        height=750,
        scrolling=False
    )

st.caption(
    "Demonstration using simulated heartbeat data. "
    "No therapeutic effect has been established."
)

from pathlib import Path

# Permanent demonstration assets
demo_folder = Path(__file__).resolve().parent / "demo_assets"

st.divider()
st.header("🌍 Earth Circle — Demonstration")

st.info(
    "Concept demonstration: Earth Circle is a proposed future "
    "private network for astronaut-approved family and friends. "
    "The media below are illustrative examples, not real astronaut communications."
)

photo_path = demo_folder / "anastasia_ai.png"
video_path = demo_folder / "demo_alex_message.mp4"

st.subheader("📸 A Memory from Home")
if photo_path.is_file():
    st.image(str(photo_path), width=350)
    st.caption("AI-generated illustrative image — fictional character Anastasia.")
else:
    st.warning("Demo image is not available.")

st.subheader("🎥 A Message from a University Friend")
if video_path.is_file():
    st.video(str(video_path), width=350)
    st.caption("Staged demonstration message from Alex, a university friend.")
else:
    st.warning("Demo video is not available.")


# ============================================================
# EARTHLINK-AI | Real ECG to Three Musical Interpretations
# Data: PhysioNet MIT-BIH Arrhythmia Database, Record 100
# Research demonstration only — not clinical therapy.
# ============================================================

import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import wfdb
from pathlib import Path
from scipy.io import wavfile

st.divider()
st.header("💓 Heartbeat to Music — Real ECG Demonstration")

st.info(
    "This demonstration uses a real, anonymized research ECG "
    "from PhysioNet (MIT-BIH Arrhythmia Database, Record 100). "
    "It is NOT the heartbeat of an astronaut's family member."
)

@st.cache_data
def load_ecg_demo():
    path = Path(__file__).resolve().parent / "ecg_data" / "100"
    record = wfdb.rdrecord(str(path))
    annotations = wfdb.rdann(str(path), "atr")

    fs = int(record.fs)
    signal = record.p_signal[:, 0]

    # Use the first 30 seconds.
    duration = 30
    segment = signal[:fs * duration]

    # Beat positions are taken from expert annotations.
    beats = np.asarray([
        s for s, symbol in zip(
            annotations.sample, annotations.symbol
        )
        if s < len(segment) and symbol in {"N", "L", "R", "A", "V", "F", "e", "j"}
    ], dtype=int)

    return fs, segment, beats

def make_heartbeat_music(beat_times, style, sample_rate=22050):
    duration = 30.0
    total = int(duration * sample_rate)
    audio = np.zeros(total, dtype=np.float64)

    styles = {
        "Calm Ambient": {
            "notes": [220.00, 261.63, 329.63, 392.00],
            "length": 1.4,
            "volume": 0.22,
        },
        "Warm Piano-like": {
            "notes": [261.63, 329.63, 392.00, 523.25],
            "length": 0.65,
            "volume": 0.30,
        },
        "Cosmic Pulse": {
            "notes": [110.00, 164.81, 220.00, 329.63],
            "length": 0.38,
            "volume": 0.32,
        },
    }

    cfg = styles[style]

    for i, beat_time in enumerate(beat_times):
        start = int(float(beat_time) * sample_rate)
        if start >= total:
            continue

        length = min(
            int(cfg["length"] * sample_rate),
            total - start
        )
        if length <= 0:
            continue

        t = np.arange(length) / sample_rate
        frequency = cfg["notes"][i % len(cfg["notes"])]

        if style == "Calm Ambient":
            tone = (
                np.sin(2 * np.pi * frequency * t)
                + 0.25 * np.sin(2 * np.pi * frequency * 2 * t)
            )
            envelope = np.minimum(t / 0.12, 1.0) * np.exp(-2.0 * t)

        elif style == "Warm Piano-like":
            tone = (
                np.sin(2 * np.pi * frequency * t)
                + 0.35 * np.sin(2 * np.pi * frequency * 2 * t)
                + 0.12 * np.sin(2 * np.pi * frequency * 3 * t)
            )
            envelope = np.exp(-5.0 * t)

        else:
            tone = (
                np.sin(2 * np.pi * frequency * t)
                + 0.35 * np.sin(2 * np.pi * (frequency / 2) * t)
            )
            envelope = np.exp(-9.0 * t)

        audio[start:start + length] += (
            cfg["volume"] * tone * envelope
        )

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.85

    pcm = (audio * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm)
    return buffer.getvalue()



def make_real_instruments_music(beat_times, instrument="Fusion", sample_rate=22050):
    from scipy.signal import resample_poly
    from math import gcd

    duration = 30.0
    total = int(duration * sample_rate)
    audio = np.zeros(total, dtype=np.float64)

    sample_dir = Path(__file__).resolve().parent / "music_samples"

    
    harp_specs = [
        ("373556_", 0.20),
        ("373563_", 0.22),
        ("373565_", 0.20),
        ("373568_", 0.20),
    ]

    handpan_specs = [
        ("587401_", 0.14),
        ("587412_", 0.14),
        ("587414_", 0.14),
        ("587415_", 0.14),
        ("587418_", 0.14),
        ("692829_", 0.12),
    ]

    if instrument == "Harp":
        sample_specs = harp_specs
    elif instrument == "Handpan":
        sample_specs = handpan_specs
    else:
        sample_specs = harp_specs + handpan_specs


    samples = []

    for prefix, volume in sample_specs:
        matches = sorted(sample_dir.glob(prefix + "*.wav"))

        if not matches:
            raise FileNotFoundError(
                f"Missing WAV sample beginning with {prefix}"
            )

        fs, sound = wavfile.read(str(matches[0]))
        sound = np.asarray(sound, dtype=np.float64)

        if sound.ndim == 2:
            sound = sound.mean(axis=1)

        peak = np.max(np.abs(sound))
        if peak > 0:
            sound = sound / peak

        divisor = gcd(int(fs), sample_rate)
        sound = resample_poly(
            sound,
            sample_rate // divisor,
            int(fs) // divisor
        )

        peak = np.max(np.abs(sound))
        if peak > 0:
            sound = sound / peak

        samples.append((sound, volume))

    for i, beat_time in enumerate(beat_times):
        start = int(float(beat_time) * sample_rate)

        if start < 0 or start >= total:
            continue

        # Play real instrument samples at ECG heartbeat times.
        sound, volume = samples[i % len(samples)]

        length = min(len(sound), total - start)
        if length <= 0:
            continue

        audio[start:start + length] += volume * sound[:length]

    # Smooth beginning and ending.
    fade = int(0.5 * sample_rate)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.85

    pcm = (audio * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, pcm)

    return buffer.getvalue()


try:
    fs_ecg, ecg_signal, beat_samples = load_ecg_demo()
    beat_times = beat_samples / fs_ecg

    st.success("Real ECG successfully loaded from PhysioNet!")

    st.subheader("1. Original ECG Signal")

    # Display the first 10 seconds for clarity.
    display_seconds = 10
    display_count = fs_ecg * display_seconds
    times = np.arange(display_count) / fs_ecg

    fig, ax = plt.subplots(figsize=(11, 3))
    ax.plot(
        times,
        ecg_signal[:display_count],
        linewidth=0.9,
        color="#1677b8"
    )

    visible_beats = beat_samples[
        beat_samples < display_count
    ]

    ax.scatter(
        visible_beats / fs_ecg,
        ecg_signal[visible_beats],
        color="#dc3545",
        s=18,
        label="Annotated heartbeats"
    )

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("ECG amplitude (mV)")
    ax.set_title("Real ECG — MIT-BIH Record 100")
    ax.legend()
    ax.grid(alpha=0.2)

    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Red markers indicate heartbeat positions from "
        "the PhysioNet reference annotations."
    )

    st.subheader("2. Heartbeat Analysis")

    rr_intervals = np.diff(beat_times)
    if len(rr_intervals) > 0:
        mean_hr = 60 / np.mean(rr_intervals)

        col1, col2, col3 = st.columns(3)
        col1.metric("Heartbeats detected", len(beat_times))
        col2.metric("Average heart rate", f"{mean_hr:.1f} bpm")
        col3.metric(
            "Mean RR interval",
            f"{np.mean(rr_intervals):.3f} s"
        )

   
        st.subheader("3. Real Instrument Music — ECG Rhythm")

        st.write(
            "Three musical versions using real harp and handpan samples. "
            "Each note follows the heartbeat timing from the ECG."
        )

        for instrument in ["Harp", "Handpan", "Combined"]:
            st.markdown(f"**🎵 Real {instrument}**")

            wav_data = make_real_instruments_music(
                beat_times, instrument
            )

            st.audio(wav_data, format="audio/wav")

            st.download_button(
                label=f"Download Real {instrument}",
                data=wav_data,
                file_name=f"EARTHLINK_AI_{instrument.lower()}.wav",
                mime="audio/wav",
                key=f"download_real_{instrument.lower()}"
            )

        
    
    
        "Scientific note: ECG-derived musical mapping is "
        "an exploratory sonification technique. No clinical "
        "or psychological therapeutic effect is claimed. "
        "Future personalized use would require consent, "
        "privacy safeguards and controlled evaluation."
    

    st.markdown(
        "Data source: [PhysioNet MIT-BIH Arrhythmia Database]"
        "(https://physionet.org/content/mitdb/1.0.0/)"
    )

except Exception as exc:
    st.error(f"ECG demonstration could not load: {exc}")

# EARTH VOICES — Interactive two-way communication prototype
st.divider()
st.header("🌍 Earth Voices — Messages from Earth")

st.write(
    "A proposed, moderated connection between astronauts and "
    "students, young researchers, and space enthusiasts worldwide. "
    "Astronauts can read and reply whenever they choose."
)

st.info(
    "Interactive demonstration only. All messages and senders are "
    "fictional. No messages are transmitted to or from astronauts."
)

earth_messages = [
    {
        "sender": "Sara — Medical Student, Romania",
        "message": (
            "Your mission inspires me to study space medicine. "
            "Thank you for showing us what is possible!"
        ),
    },
    {
        "sender": "Arman — High School Student, Iran",
        "message": (
            "My dream is to become an astronaut one day. "
            "Watching your journey gives me hope!"
        ),
    },
    {
        "sender": "Mei — Space Science Student, Singapore",
        "message": (
            "Even from Earth, we are cheering for you. "
            "Your work inspires the next generation of explorers!"
        ),
    },
]

selected_message = st.selectbox(
    "Choose a message from Earth:",
    range(len(earth_messages)),
    format_func=lambda i: earth_messages[i]["sender"],
    key="earth_voices_selection",
)

st.markdown(
    f"**Message:** {earth_messages[selected_message]['message']}"
)

reply = st.text_area(
    "Astronaut's optional reply (simulation):",
    placeholder="Write a supportive reply...",
    key=f"earth_voices_reply_{selected_message}",
)

if st.button("Preview Reply", key="earth_voices_preview"):
    if reply.strip():
        st.success("Reply preview — not actually sent.")
        st.write(reply)
    else:
        st.warning("Write a reply first.")

st.caption(
    "Future concept: invitation or eligibility screening, content "
    "moderation, astronaut-controlled message frequency, optional "
    "asynchronous replies, consent, and communication safeguards."
)

# EARTH VOICES — Voice and video demonstrations
st.subheader("🎙️ Voice & Video Messages from Earth")

st.caption(
    "Fictional demonstration content. "
    "No real messages are sent to astronauts."
)

from pathlib import Path

earth_voice_video = (
    Path(__file__).resolve().parent
    / "demo_assets"
    / "earth_voices_sara.mp4"
)

st.markdown("**🎥 Example video message from Earth**")

if earth_voice_video.is_file():
    st.video(str(earth_voice_video), width=350)
    st.caption("Staged demonstration video — fictional sender.")
else:
    st.warning("Example video is not available.")

