import threading
import sys
import time
import wave
import io
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import speech_recognition as sr
from speech_recognition import AudioData

FILENAME_WAV = "speech.wav"
FILENAME_TXT = "speech.txt"
RATE = 16000 
CHUNK = 1024

stop_event = threading.Event()

def wait_for_enter():
    input() 
    stop_event.set()

def record_mic():
    """Starts recording as soon as the script runs."""
    stop_event.clear()
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    print("\nRecording... Press Enter to stop.")
    
    threading.Thread(target=wait_for_enter, daemon=True).start()

    chars = '|/-\\'
    idx = 0
    while not stop_event.is_set():
        frames.append(stream.read(CHUNK, exception_on_overflow=False))
        sys.stdout.write(f'\r{chars[idx % 4]} Recording...')
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)

    print("\nRecording stopped.")
    stream.stop_stream()
    stream.close()
    width = p.get_sample_size(pyaudio.paInt16)
    p.terminate()
    return b''.join(frames), width

def save_and_transcribe(data, width):
    """Saves raw audio to .wav and transcription to .txt."""
    with wave.open(FILENAME_WAV, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(RATE)
        wf.writeframes(data)
    print(f"💾 Saved raw audio as: {FILENAME_WAV}")

    recognizer = sr.Recognizer()
    audio_obj = AudioData(data, RATE, width)
    
    try:
        text = recognizer.recognize_google(audio_obj)
        print(f"Transcription: {text}")

        with open(FILENAME_TXT, "w") as f:
            f.write(text)
        print(f"Saved transcription as: {FILENAME_TXT}")
    except sr.UnknownValueError:
        print("AI could not understand the audio.")
    except sr.RequestError as e:
        print(f"API Error: {e}")

def show_waveform(data):
    """Displays the waveform in a Matplotlib window."""
    samples = np.frombuffer(data, dtype=np.int16)
    time_axis = np.linspace(0, len(samples) / RATE, num=len(samples))

    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color='#2c3e50')
    plt.title("Your Voice Waveform Visualization")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    print("="*40)
    print("✨ YOUR MINI SPEECH-TO-TEXT STUDIO ✨")
    print("="*40)
    
    audio_data, sample_width = record_mic()
    
    save_and_transcribe(audio_data, sample_width)
    
    show_waveform(audio_data)

if __name__ == "__main__":
    main()