import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr

def play_audio(file_path):
    sample_rate, audio_data = wav.read(file_path)
    sd.play(audio_data, sample_rate)
    sd.wait()

def record_response(output_file):
    duration = 5  # Duration of the user's response in seconds
    sample_rate = 44100  # Sample rate of the audio
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    wav.write(output_file, sample_rate, np.int16(recording * 32767))
    print("Recording saved as", output_file)

if __name__ == '__main__':
    # text = "Hello There"
    # create_speech_from_text(text)

    # Play audio from a recording
    # question_path = r"C:\Users\ML-2\Documents\GitHub\UWBE\recordings\questions\recording_1.wav"
    # play_audio(question_path)
    # Save the patient's response
    response_path = r"C:\Users\ML-2\Documents\GitHub\UWBE\recordings\responses\recording_1.wav"
    record_response(response_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(response_path) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    print("Recognized text:", text)
