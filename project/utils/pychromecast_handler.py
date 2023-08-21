"""
Class for handling the connection to the Google Mini
"""

import pychromecast
import config

class PychromecastPlayer:
    def __init__(self):
        self.mc = None
        self.cast = None
        self.get_chromecast()

    def get_chromecast(self):
        # Try connecting to chromecast directly
        try:
            cast = pychromecast.Chromecast(config.CAST_IP)
            cast.wait()
            print(cast)
            self.cast = cast
            self.mc = self.cast.media_controller
            return
        except:
            print("Connection attempt failed. Retrying...", end="\n")

        # Scan network for all chromecasts and search for chromecast by uuid
        try:
            chromecasts, services = pychromecast.get_chromecasts()
            for chromecast in chromecasts:
                if str(chromecast.device.uuid) == config.CAST_UUID:
                    cast = chromecast
                    cast.wait()
                    print(f"Connection Successful: {cast}")
                    self.cast = cast
                    self.mc = self.cast.media_controller
                    return
        except Exception as e:
            print(e)
            print("Failed to get chromecast")
    def play_url(self, url):
        self.mc.play_media(url=url, content_type='audio/mp3')
        self.mc.block_until_active()
        self.mc.play()