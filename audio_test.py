import time
import pychromecast
import config

"""
Test the Google mini audio
"""

if __name__ == '__main__':
    # Try connecting to chromecast directly
    try:
        cast = pychromecast.Chromecast(config.IPV4_ADDRESS)
        cast.wait()
        mc = cast.media_controller
        mc.play_media(url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", content_type='audio/mp3')
        mc.block_until_active()
        mc.play()
        time.sleep(3)
        mc.pause()
    except Exception as e:
        print(e)
        print("Connection attempt failed. Retrying...", end="\n")

    # Scan network for all chromecasts and search for chromecast by uuid
    try:
        chromecasts, services = pychromecast.get_chromecasts()
        for chromecast in chromecasts:
            if str(chromecast.device.uuid) == config.CAST_UUID:
                cast = chromecast
                cast.wait()
                mc = cast.media_controller
                mc.play_media(url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                                                 content_type='audio/mp3')
                mc.block_until_active()
                mc.play()
                time.sleep(3)
                mc.pause()
                print("Connection Successful")
                break
    except Exception as e:
        print(e)
        print("Failed to get chromecast")






