import datetime

def get_timestamp(unix_time):
    local_datetime = datetime.datetime.fromtimestamp(unix_time)
    return \
        f"{local_datetime.strftime('%Y')}-" \
        f"{local_datetime.strftime('%m')}-" \
        f"{local_datetime.strftime('%d_T')}" \
        f"{local_datetime.strftime('%H')}-" \
        f"{local_datetime.strftime('%M')}-" \
        f"{local_datetime.strftime('%S')}"