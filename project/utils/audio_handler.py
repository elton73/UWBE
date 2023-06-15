
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import file_handler

class AudioHandler:
    def __init__(self):
        self.speech_recognizer = sr.Recognizer()
        self.duration = 10
        self.sample_rate = 44100
        self.silence_threshold = 4
        self.output_file_directory = r"C:\Users\ML-2\Documents\GitHub\UWBE\recordings\responses"
        self.output_file = None

        #debug
        self.audio_buffer = []
        self.end = None
        self.current = None

    def play_audio(self, audio_file):
        sample_rate, audio_data = wav.read(audio_file)
        sd.play(audio_data, sample_rate)
        sd.wait()

    def record_audio(self):
        self.current = time.time()
        self.end = time.time() + self.silence_threshold

        while self.current <= self.end:
            recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
            print(recording)



        print("Recording...")
        recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
        sd.wait()
        self.output_file = file_handler.generate_audio_output_file()
        wav.write(self.output_file, self.sample_rate, np.int16(recording * 32767))
        print("Recording saved as", self.output_file)

    def audio_to_text(self):
        with sr.AudioFile(self.output_file) as source:
            audio = self.speech_recognizer.record(source)
        text = self.speech_recognizer.recognize_google(audio)
        if text:
            print("Recognized text:", text)
            return True
        return False

if __name__ == '__main__':
    a = AudioHandler()