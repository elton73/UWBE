import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import os
import sys
from project.utils.timestamps import get_timestamp


class AudioHandler():
    def __init__(self):
        #  Directories
        self.root_directory = sys.path[1]
        self.audio_directory = os.path.join(self.root_directory, "audio")
        self.output_directory = os.path.join(self.root_directory, "responses")
        self.output_file = None

        #  Audio Settings
        self.fs = 48000
        self.channels = 2
        self.duration = 5  # seconds
        self.recognizer = sr.Recognizer()
        self.audio_data = None

        #  Questions
        self.question_counter = 1

        #  User responses
        self.text = None
        self.responses = []

    def run(self):
        recording_complete_flag = False

        self.play_introduction()
        while not recording_complete_flag:
            # ask user a question
            self.ask_question()
            # listen to user response. If no response can be found or the user says repeat, ask again
            failures = 0
            listen_success_flag = False
            while not listen_success_flag:
                # record user response and save recording to text
                listen_success_flag = self.listen()
                if not listen_success_flag:
                    failures += 1
                    if failures > 3:
                        print("Failed to get response 3 times")
                        return
                    self.ask_user_to_repeat_answer()
                elif "reset" in self.text:
                    #  User asks for a reset. Set all variables to default.
                    self.delete_user_responses()
                    self.start_over()
                    self.play_introduction()

                elif "repeat" in self.text:
                    self.repeat_question()
                    self.ask_question()
                    listen_success_flag = False

                else:
                    self.say_thanks()
                    self.save_response()
                    self.question_counter += 1
                    if self.question_counter > 3:
                        self.say_final_thanks()
                        recording_complete_flag = True
                    else:
                        self.next_question()

        print(self.responses)

    def listen(self):
        self.audio_data = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=self.channels)
        sd.wait()

        self.output_file = os.path.join(self.output_directory, get_timestamp())
        wav.write(self.output_file, self.fs, np.int16(self.audio_data * 32767))  # scale audio data to 16-bit int
        success_flag = self.audio_to_text()
        return success_flag

    def audio_to_text(self):
        try:
            with sr.AudioFile(self.output_file) as source:
                audio = self.recognizer.record(source, duration=len(self.audio_data) / self.fs)
                self.text = self.recognizer.recognize_google(audio)
                return True
        except sr.UnknownValueError:
            return False

    def get_question(self):
        if self.question_counter == 1:
            return os.path.join(self.audio_directory, "questions", "name.wav")
        elif self.question_counter == 2:
            return os.path.join(self.audio_directory, "questions", "date.wav")
        elif self.question_counter == 3:
            return os.path.join(self.audio_directory, "questions", "riddle.wav")
        return "q"

    def play_introduction(self):
        self.broadcast(os.path.join(self.audio_directory, "intro", "introduction_1.wav"))

    def ask_user_to_repeat_answer(self):
        self.broadcast(os.path.join(self.audio_directory, "repeat", "repeat_2.wav"))

    def repeat_question(self):
        self.broadcast(os.path.join(self.audio_directory, "repeat", "repeat_1.wav"))

    def say_thanks(self):
        self.broadcast(os.path.join(self.audio_directory, "thanks", "thank_you_1.wav"))

    def say_final_thanks(self):
        self.broadcast(os.path.join(self.audio_directory, "thanks", "final_thanks_1.wav"))

    def next_question(self):
        self.broadcast(os.path.join(self.audio_directory, "next", "next_1.wav"))

    def ask_question(self):
        self.broadcast(self.get_question())

    def start_over(self):
        self.broadcast(os.path.join(self.audio_directory, "reset", "start_over_1.wav"))

    def save_response(self):
        self.responses.append(self.text)

    def delete_user_responses(self):
        self.responses = []
        self.question_counter = 1

    @staticmethod
    def broadcast(audio_file):
        try:
            sample_rate, audio_data = wav.read(audio_file)
            sd.play(audio_data, sample_rate)
            sd.wait()
        except FileNotFoundError:
            print("File not Found")
            return "q"
        except Exception as e:
            print(e)
            return "q"


if __name__ == '__main__':
    a = AudioHandler()
    a.run()
