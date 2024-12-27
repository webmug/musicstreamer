import socket
import json
from zeroconf import ServiceBrowser, Zeroconf

class GoogleHomeListener:
    def __init__(self):
        self.devices = []

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            self.devices.append({
                'name': name.split('.')[0],
                'address': address,
                'port': info.port
            })

def find_google_devices():
    zc = Zeroconf()
    listener = GoogleHomeListener()
    browser = ServiceBrowser(zc, "_googlecast._tcp.local.", listener)
    
    try:
        print("Searching for Google Home devices (5 seconds)...")
        import time
        time.sleep(5)
    finally:
        zc.close()
    
    return listener.devices

if __name__ == "__main__":
    devices = find_google_devices()
    print("\nFound devices:")
    print(json.dumps(devices, indent=2))