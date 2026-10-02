import math
import struct
import wave

sample_rate = 44100
duration = 35.0  # 35 seconds
total_samples = int(sample_rate * duration)

bpm = 85.0
beat_sec = 60.0 / bpm

# Frequencies for chords (Cmaj7 -> Am7 -> Dm7 -> G7)
# Cmaj7: C4, E4, G4, B4
# Am7:   A3, C4, E4, G4
# Dm7:   D4, F4, A4, C5
# G7:    G3, B3, D4, F4

chord_freqs = [
    [261.63, 329.63, 392.00, 493.88],  # Cmaj7
    [220.00, 261.63, 329.63, 392.00],  # Am7
    [293.66, 349.23, 440.00, 523.25],  # Dm7
    [196.00, 246.94, 293.66, 349.23],  # G7
]

bass_freqs = [130.81, 110.00, 146.83, 98.00]  # C3, A2, D3, G2

output_samples = []

for i in range(total_samples):
    t = i / float(sample_rate)
    
    # Determine bar index (4 beats per bar)
    bar_time = (t % (beat_sec * 16)) / (beat_sec * 4)
    chord_idx = int(bar_time) % 4
    
    # Time inside current beat
    beat_t = t % beat_sec
    beat_num = int(t / beat_sec) % 4

    # 1. Soft Piano / Rhodes Chords
    chord_signal = 0.0
    freqs = chord_freqs[chord_idx]
    # Slow decay per chord bar
    bar_decay = math.exp(-1.5 * ((t % (beat_sec * 4)) / (beat_sec * 4)))
    for f in freqs:
        # Add slight tremolo and warmth
        tremolo = 1.0 + 0.15 * math.sin(2 * math.pi * 5.0 * t)
        sine = math.sin(2 * math.pi * f * t)
        harm2 = 0.3 * math.sin(2 * math.pi * f * 2.0 * t)
        chord_signal += (sine + harm2) * tremolo
    chord_signal = (chord_signal / len(freqs)) * bar_decay * 0.25

    # 2. Warm Bass
    bass_f = bass_freqs[chord_idx]
    bass_decay = math.exp(-2.0 * (beat_t / beat_sec)) if beat_num in [0, 2] else 0.2
    bass_signal = math.sin(2 * math.pi * bass_f * t) * bass_decay * 0.35

    # 3. Lo-Fi Drums (Kick, Snare, Hi-Hat)
    kick = 0.0
    snare = 0.0
    hihat = 0.0

    # Kick on beat 0 and 2.5
    if beat_num == 0 or (beat_num == 2 and beat_t > beat_sec * 0.4):
        k_t = beat_t if beat_num == 0 else (beat_t - beat_sec * 0.5)
        if 0 <= k_t < 0.15:
            f_kick = 110.0 * math.exp(-25.0 * k_t)
            kick = math.sin(2 * math.pi * f_kick * k_t) * math.exp(-12.0 * k_t) * 0.4

    # Snare on beat 1 and 3
    if beat_num in [1, 3] and beat_t < 0.15:
        # White noise burst + tone
        noise = (math.sin(t * 12345.67) * 43758.5453) % 1.0 - 0.5
        snare = noise * math.exp(-20.0 * beat_t) * 0.25

    # Hi-hat on every 8th note
    hat_t = t % (beat_sec / 2)
    if hat_t < 0.05:
        noise = (math.sin(t * 98765.43) * 12345.67) % 1.0 - 0.5
        hihat = noise * math.exp(-60.0 * hat_t) * 0.12

    # Vinyl crackle / hiss
    crackle = ((math.sin(t * 7777.7) * 9999.9) % 1.0 - 0.5) * 0.015

    # Mix
    mix = chord_signal + bass_signal + kick + snare + hihat + crackle
    
    # Soft limiter / clamp
    mix = max(-0.95, min(0.95, mix))
    
    # Convert to 16-bit PCM integer
    sample_val = int(mix * 32767.0)
    output_samples.append(sample_val)

# Write WAV file
wav_file = wave.open("lofi_music.wav", "w")
wav_file.setnchannels(1)  # Mono
wav_file.setsampwidth(2)  # 16-bit
wav_file.setframerate(sample_rate)

packed_data = bytearray()
for s in output_samples:
    packed_data.extend(struct.pack("<h", s))

wav_file.writeframes(packed_data)
wav_file.close()
print("Successfully generated lofi_music.wav!")
