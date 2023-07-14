import os

def wlan_ip():
    import subprocess
    result = subprocess.run('ipconfig', stdout=subprocess.PIPE, text=True).stdout.lower()
    scan = 0
    for i in result.split('\n'):
        if 'wireless' in i: scan = 1
        if scan:
            if 'ipv4' in i: return i.split(':')[1].strip()

# TAG_ID = os.getenv("TAG_ID")
TAG_ID = "200000652"
PROJECT_DIRECTORY = os.getenv("PROJECT_DIRECTORY") #Example C:\Users\{user}\Documents\GitHub\UWBE
IPV4_ADDRESS = wlan_ip()
CAST_IP = os.getenv("CAST_IP")
CAST_UUID = os.getenv("CAST_UUID")

"""
Pozyx Connection
"""
tenant_id = os.environ.get("POZYX_TENANT_ID")
api_key = os.environ.get("POZYX_API_KEY")
host = "mqtt.cloud.pozyxlabs.com"
port = 443
topic = f"{tenant_id}/tags"
username = tenant_id
password = api_key

