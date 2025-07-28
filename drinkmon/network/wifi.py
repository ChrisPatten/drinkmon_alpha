"""
WiFi connection and AP setup.
Implements connect_wifi and start_ap functions.
"""
import network
import utime as time

def connect_wifi(ssid, pw, timeout=15):
    """
    Connect to WiFi using provided SSID and password.
    Returns True if connected, False otherwise.
    """
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(ssid, pw)
        for _ in range(timeout):
            if sta.isconnected():
                print("WiFi connected, IP:", sta.ifconfig()[0])
                return True
            time.sleep(1)
    return sta.isconnected()

def start_ap():
    """
    Start Access Point for captive portal configuration.
    """
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32-Setup')
    print('Started AP, connect to WiFi "ESP32-Setup" and browse to http://192.168.4.1')
