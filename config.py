import os

def wlan_ip():
    import subprocess
    result = subprocess.run('ipconfig', stdout=subprocess.PIPE, text=True).stdout.lower()
    scan = 0
    for i in result.split('\n'):
        if 'wireless' in i: scan = 1
        if scan:
            if 'ipv4' in i: return i.split(':')[1].strip()

TAG_ID = os.getenv("TAG_ID")
PROJECT_DIRECTORY = os.getenv("PROJECT_DIRECTORY")
IPV4_ADDRESS = wlan_ip()
CAST_UUID = os.getenv("CAST_UUID")

