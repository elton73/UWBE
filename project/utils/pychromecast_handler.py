import pychromecast
import inspect


class AudioPlayer:
    def __init__(self):
        self.cast = self.get_chromecast()
        self.mc = self.cast.media_controller
    def get_chromecast(self):
        cast = pychromecast.Chromecast("192.168.0.102")
        cast.wait()
        print(cast)
        # if cast[0]:
        #     print(f"Connecting to {cast[0]}")
        # else:
        #     print("Can't Connect to chromecast")
        return cast

    def play_url(self, url):
        self.mc.play_media(url=url, content_type='audio/mp3')
        self.mc.block_until_active()
        self.mc.play()

if __name__ == '__main__':
    a = AudioPlayer()
    a.play_url("http://192.168.0.103:5000/static/recording_1.mp3")