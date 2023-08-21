"""
Format a unix_timestamp to be easier to read
"""

import datetime
import time

def get_timestamp(unix_time=None):
    if not unix_time:
        unix_time = time.time()
    local_datetime = datetime.datetime.fromtimestamp(unix_time)
    return \
        f"{local_datetime.strftime('%Y')}-" \
        f"{local_datetime.strftime('%m')}-" \
        f"{local_datetime.strftime('%d_T')}" \
        f"{local_datetime.strftime('%H')}-" \
        f"{local_datetime.strftime('%M')}-" \
        f"{local_datetime.strftime('%S')}"