import network
import time

def connect_wifi(ssid, password, timeout=15):
    """Connect to WiFi network with timeout"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print('Already connected to WiFi')
        print('Network config:', wlan.ifconfig())
        return wlan
    
    print(f'Connecting to WiFi: {ssid}...')
    wlan.connect(ssid, password)
    
    start_time = time.time()
    while not wlan.isconnected():
        if time.time() - start_time > timeout:
            print('WiFi connection timeout')
            return None
        time.sleep(0.1)
    
    print('WiFi connected!')
    print('Network config:', wlan.ifconfig())
    return wlan

def start_access_point(essid="NFC-SETUP", password="12345678"):
    """Start ESP32 as Access Point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=essid, password=password)
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f'Access Point started: {essid}')
    print('AP config:', ap.ifconfig())
    return ap

def is_wifi_connected(wlan):
    """Check if WiFi is connected"""
    return wlan is not None and wlan.isconnected()
