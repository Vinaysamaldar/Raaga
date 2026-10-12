import math
import os
import struct
import wave

OUTPUT_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 22050
DURATION_SEC = 24  # 24-second seamless loopable musical arrangement per style

# Musical styles / Ragas in Hz (Carnatic & Sandalwood scales)
STYLES = {
    "mass_2026": {
        "root": 146.83,  # D3
        "scale": [293.66, 329.63, 349.23, 392.00, 440.00, 466.16, 523.25, 587.33],
        "pattern": [0, 3, 4, 6, 4, 3, 2, 0, 4, 7, 6, 4, 3, 2, 1, 0],
        "tempo_bpm": 128,
        "vibrato": 4.5,
    },
    "melody": {
        "root": 130.81,  # C3 (Raga Mohanam / Kalyani feel)
        "scale": [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25],
        "pattern": [0, 1, 2, 3, 4, 5, 4, 3, 2, 4, 3, 1, 2, 1, 0, 0],
        "tempo_bpm": 96,
        "vibrato": 5.5,
    },
    "bhavageethe": {
        "root": 146.83,  # D3 (Raga Hamsadhwani / Abheri)
        "scale": [293.66, 329.63, 370.00, 440.00, 554.37, 587.33, 440.00, 370.00],
        "pattern": [0, 1, 2, 3, 4, 5, 4, 3, 2, 3, 1, 2, 0, 1, 0, 0],
        "tempo_bpm": 84,
        "vibrato": 6.0,
    },
    "janapada": {
        "root": 164.81,  # E3 (Upbeat Folk Pentatonic)
        "scale": [329.63, 370.00, 415.30, 493.88, 554.37, 659.25, 554.37, 493.88],
        "pattern": [0, 2, 3, 4, 5, 4, 3, 2, 3, 3, 2, 1, 2, 0, 1, 0],
        "tempo_bpm": 132,
        "vibrato": 5.0,
    },
    "devotional": {
        "root": 130.81,  # C3 (Raga Kapi / Yamuna Kalyani)
        "scale": [261.63, 293.66, 311.13, 349.23, 392.00, 440.00, 466.16, 523.25],
        "pattern": [0, 2, 3, 4, 6, 7, 6, 4, 3, 4, 2, 1, 0, 2, 1, 0],
        "tempo_bpm": 88,
        "vibrato": 5.2,
    },
    "rajyotsava": {
        "root": 146.83,  # D3 (Majestic Anthem)
        "scale": [293.66, 329.63, 370.00, 392.00, 440.00, 493.88, 554.37, 587.33],
        "pattern": [0, 2, 4, 7, 6, 4, 5, 4, 3, 2, 4, 3, 2, 1, 0, 0],
        "tempo_bpm": 112,
        "vibrato": 4.8,
    },
    "carnatic": {
        "root": 138.59,  # C#3 (Classical Veena + Tanpura)
        "scale": [277.18, 311.13, 349.23, 415.30, 466.16, 554.37, 622.25, 554.37],
        "pattern": [0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 4, 2, 3, 1, 2, 0],
        "tempo_bpm": 92,
        "vibrato": 6.2,
    },
}


def generate_track(name, cfg):
    filepath = os.path.join(OUTPUT_DIR, f"{name}.wav")
    total_samples = SAMPLE_RATE * DURATION_SEC
    root = cfg["root"]
    fifth = root * 1.4983  # Pa (Perfect Fifth)
    scale = cfg["scale"]
    pattern = cfg["pattern"]
    beat_sec = 60.0 / cfg["tempo_bpm"]
    note_dur = beat_sec  # 1 beat per melodic note

    frames = bytearray()
    phase_melody = 0.0

    for i in range(total_samples):
        t = i / SAMPLE_RATE

        # 1. Continuous Warm Tanpura / Harmonium Pad (Sa - Pa - Sa)
        tanpura = (
            0.14 * math.sin(2.0 * math.pi * root * t)
            + 0.09 * math.sin(2.0 * math.pi * fifth * t)
            + 0.06 * math.sin(2.0 * math.pi * (root * 2.0) * t)
            + 0.03 * math.sin(2.0 * math.pi * (root * 3.0) * t)
        )
        # Gentle breathing modulation on the drone
        tanpura *= 0.85 + 0.15 * math.sin(2.0 * math.pi * 0.25 * t)

        # 2. Expressive Flute / Veena Lead Melody with smooth legato & gamaka vibrato
        note_idx = int(t / note_dur)
        note_pos = (t % note_dur) / note_dur  # 0.0 to 1.0 within note
        target_freq = scale[pattern[note_idx % len(pattern)]]

        # Gamaka (Indian classical pitch oscillation)
        gamaka = 1.0 + 0.008 * math.sin(2.0 * math.pi * cfg["vibrato"] * t)
        inst_freq = target_freq * gamaka
        phase_melody += 2.0 * math.pi * inst_freq / SAMPLE_RATE

        # Smooth ADSR envelope (no clicks!)
        if note_pos < 0.12:
            env = math.sin((note_pos / 0.12) * (math.pi / 2.0))
        elif note_pos > 0.85:
            env = math.cos(((note_pos - 0.85) / 0.15) * (math.pi / 2.0))
        else:
            env = 1.0 - 0.15 * (note_pos - 0.12)

        # Rich harmonic timbre (Flute + Veena overtones)
        melody = env * (
            0.32 * math.sin(phase_melody)
            + 0.14 * math.sin(2.0 * phase_melody)
            + 0.06 * math.sin(3.0 * phase_melody)
        )

        # 3. Warm Bassline pulse on every 2 beats
        bass_pos = (t % (beat_sec * 2.0)) / (beat_sec * 2.0)
        bass_env = math.exp(-3.5 * bass_pos) * math.sin(min(1.0, bass_pos * 25.0) * (math.pi / 2.0))
        bass_freq = root if (int(t / (beat_sec * 2.0)) % 2 == 0) else fifth * 0.5
        bass = 0.22 * bass_env * math.sin(2.0 * math.pi * bass_freq * t)

        # 4. Soft Tabla / Mridangam tonal percussion on each beat
        beat_pos = (t % beat_sec) / beat_sec
        tabla_env = math.exp(-9.0 * beat_pos) * math.sin(min(1.0, beat_pos * 40.0) * (math.pi / 2.0))
        tabla_pitch = (root * 2.0) if (note_idx % 4 != 2) else (fifth * 2.0)
        tabla = 0.12 * tabla_env * math.sin(2.0 * math.pi * tabla_pitch * t)

        # Master mix + fade-in/fade-out at loop boundaries
        sample = tanpura + melody + bass + tabla
        if t < 0.25:
            sample *= t / 0.25
        elif t > DURATION_SEC - 0.25:
            sample *= (DURATION_SEC - t) / 0.25

        clamped = max(-0.95, min(0.95, sample))
        pcm_val = int(clamped * 32767)
        frames.extend(struct.pack("<h", pcm_val))

    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(bytes(frames))
    print(f"Generated {filepath} ({len(frames) // 1024} KB)")


if __name__ == "__main__":
    for style_name, style_cfg in STYLES.items():
        generate_track(style_name, style_cfg)
    print("All 7 Kannada musical audio tracks generated successfully!")
