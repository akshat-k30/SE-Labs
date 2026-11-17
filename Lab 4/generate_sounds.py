"""Generate simple sound effect WAV files for the marble maze game."""
import struct
import wave
import math
import os

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game", "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

SAMPLE_RATE = 44100

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write a list of float samples (-1..1) to a 16-bit mono WAV."""
    path = os.path.join(SOUNDS_DIR, filename)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            wf.writeframes(struct.pack('<h', int(s * 32767)))
    print(f"  Created: {path}")

def generate_bounce():
    """Short, punchy bounce sound - a quick frequency sweep down."""
    duration = 0.08  # seconds
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        envelope = 1.0 - (t / duration)  # linear fade out
        freq = 800 - 600 * (t / duration)  # sweep from 800 Hz to 200 Hz
        sample = envelope * math.sin(2 * math.pi * freq * t) * 0.6
        samples.append(sample)
    write_wav("bounce.wav", samples)

def generate_goal():
    """Happy ascending chime for reaching the goal."""
    duration = 0.6
    n = int(SAMPLE_RATE * duration)
    samples = []
    # Play a quick ascending arpeggio: C5, E5, G5
    notes = [523.25, 659.25, 783.99]
    note_dur = duration / len(notes)
    for i in range(n):
        t = i / SAMPLE_RATE
        note_idx = min(int(t / note_dur), len(notes) - 1)
        freq = notes[note_idx]
        local_t = t - note_idx * note_dur
        envelope = max(0, 1.0 - local_t / note_dur) * 0.7
        sample = envelope * math.sin(2 * math.pi * freq * local_t)
        samples.append(sample)
    write_wav("goal.wav", samples)

def generate_timeout():
    """Low descending buzz for timeout - sounds like a failure."""
    duration = 0.5
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        envelope = max(0, 1.0 - t / duration) * 0.6
        freq = 300 - 150 * (t / duration)  # descend from 300 to 150 Hz
        sample = envelope * math.sin(2 * math.pi * freq * t)
        # Add a slight buzz/roughness
        sample += envelope * 0.3 * math.sin(2 * math.pi * freq * 2 * t)
        samples.append(sample * 0.5)
    write_wav("timeout.wav", samples)

if __name__ == "__main__":
    print("Generating sound effects...")
    generate_bounce()
    generate_goal()
    generate_timeout()
    print("Done!")
