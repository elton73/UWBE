#generate new mp3 files here from text to speech (Should probably just use an online generator)

import pyttsx3
from config import PROJECT_DIRECTORY
import os
from inputs import get_mp3_file, get_text


def text_to_speech(text, output_file):
    engine = pyttsx3.init()
    engine.save_to_file(text, output_file)
    engine.runAndWait()

def main():
    user_input = get_mp3_file()
    if user_input == "q":
        return
    output_file = os.path.join(PROJECT_DIRECTORY,
                             "web_app",
                             "static",
                               user_input)
    user_input = get_text()
    if user_input == "q":
        return

    text_to_speech(user_input, output_file)
if __name__ == '__main__':
    main()


