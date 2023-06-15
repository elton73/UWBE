import os


def generate_audio_output_file():
    audio_path = r"C:\Users\ML-2\Documents\GitHub\UWBE\recordings"
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)
    counter = 1
    audio_file = os.path.join(audio_path, f"recording_{counter}.wav")
    while os.path.exists(audio_file):
        counter += 1
        audio_file = os.path.join(audio_path, f"recording_{counter}.wav")
    return audio_file
