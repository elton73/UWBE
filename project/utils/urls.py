"""
Storage for all mp3 urls that the Google Mini will play
"""

import config
def get_url(zone):
    if zone == "Living Room":
        return f"http://{config.IPV4_ADDRESS}:5000/static/LivingRoom.mp3"

    if zone == "Kitchen":
        return f"http://{config.IPV4_ADDRESS}:5000/static/Kitchen.mp3"

    if zone == "Bedroom":
        return f"http://{config.IPV4_ADDRESS}:5000/static/Bedroom.mp3"

    if zone == "Washroom":
        return f"http://{config.IPV4_ADDRESS}:5000/static/Washroom.mp3"