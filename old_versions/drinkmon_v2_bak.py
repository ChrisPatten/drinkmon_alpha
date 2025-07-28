
"""
Imports
-------
Standard library, MicroPython, and hardware-specific modules are imported here for clarity and maintainability.
"""
# Standard library imports
import sys
import math

# MicroPython/ESP32 hardware-specific imports
import network
import socket
import ujson
import machine
import utime
import os
import uasyncio as asyncio

# VL53L0X sensor driver (ensure vl53l0x.py is present)
from drinkmon.hardware.vl53l0x import VL53L0X

# HTTP request libraries (try/fallback)
try:
    import urequests
except ImportError:
    try:
        import mrequests as urequests
    except ImportError:
        print("No HTTP request library found. Please add urequests.py or mrequests.py to your project.")
        urequests = None

# Regex for URL decoding (try/fallback)
try:
    import ure
except ImportError:
    ure = None


async def button_monitor_task() -> None:
    """
    Monitor the button pin and end session if pressed.
    Debounces the button to avoid multiple triggers.
    Only ends session if currently active.
    """
    debounce_ms = 200
    last_press = 0
    global user_active, start_ts
    while True:
        if button and button.value() == 0:  # Button pressed (active low)
            now = utime.ticks_ms()
            if now - last_press > debounce_ms:
                if user_active:
                    user_active = False
                    print("Session ended by button press!")
                last_press = now
            await asyncio.sleep_ms(debounce_ms)
        else:
            await asyncio.sleep_ms(20)

I2C_SCAN_MODE = False  # Set to True to run I2C scanner and exit
LASER_DEBUG_MODE = False  # Set to True to enable laser debug mode

def i2c_scan(i2c=None) -> None:
    """
    Scan the I2C bus and print all detected device addresses.
    Useful for hardware debugging and verifying sensor connections.

    Parameters:
        i2c (machine.I2C): Optional I2C instance. If None, creates default.
    """
    print("\nI2C Scanner starting...")
    if i2c is None:
        try:
            i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL_PIN), sda=machine.Pin(I2C_SDA_PIN))
        except Exception as e:
            print(f"Failed to initialize I2C: {e}")
            return
    try:
        devices = i2c.scan()
        if not devices:
            print("No I2C devices found.")
        else:
            print(f"Found {len(devices)} device(s):")
            for addr in devices:
                print(f"  - Address: 0x{addr:02X} ({addr})")
    except Exception as e:
        print(f"I2C scan error: {e}")
    print("I2C scan complete.\n")
async def laser_debug_mode_loop() -> None:
    """
    Laser debug mode: Continuously read TOF sensor and set LED color using color_for_distance.
    Ignores all other app logic. For hardware testing and calibration.
    """
    print("Laser debug mode enabled. Showing live distance as LED color.")
    while True:
        d = None
        # Use VL53L0X API: .range property for single reading
        if tof:
            try:
                d = tof.range
            except Exception as e:
                print(f"VL53L0X read error: {e}")
                d = None
        if d is not None and d > 0:
            rgb = color_for_distance(d)
            set_color(rgb, 1.0)
        else:
            set_color((128,128,128), 0.2)
        await asyncio.sleep(0.1)
import sys
import math
import uasyncio as asyncio

"""
Button pin configuration
BUTTON_PIN: GPIO pin number for manual session end button.
"""
# Hardware pin config
I2C_SCL_PIN, I2C_SDA_PIN = 22, 21
RED_PIN, GREEN_PIN, BLUE_PIN = 19, 18, 5
BUTTON_PIN = 23  # Example pin, change as needed

PWM_FREQ, MAX_DUTY = 1000, 1023

# Button setup
try:
    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    print(f"Button initialized on pin {BUTTON_PIN}.")
except Exception as e:
    print(f"Button initialization failed: {e}")
    button = None

# App logic params
END_TIMEOUT      = (60 * 30)   # seconds
THRESH_MM        = 100  # 10 cm
SENSOR_PERIOD    = 1.0  # seconds
BREATH_PERIOD_MS = 1000 # 1s per breath
POLL_INTERVAL    = 30   # friend session poll interval (seconds)

FRIEND_POLL_URL = 'https://drinkmon.chrispatten.dev/api/friend_sessions'  # replace with your API
START_POST_URL  = 'https://drinkmon.chrispatten.dev/api/start_session'

CONFIG_FILE     = "config.json"


def load_html_template(file_path: str = "config.html") -> str:
    """
    Load the captive portal HTML template from an external file.
    
    Parameters:
    file_path (str): Path to the HTML file (default: "config.html").
    
    Returns:
    str: HTML content as a string.
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading HTML template: {e}")
        # Fallback minimal HTML
        return "<html><body><h2>Setup Page Unavailable</h2></body></html>"


# Global variable for LED hue state
_fade_led_hue = 0.0

def fade_led_spectrum(duration: float = 0.02, step_size: float = 0.002) -> None:
    """
    Fade the LED through the spectrum of colors using PWM.
    This function cycles the LED smoothly through the RGB color wheel.
    Should be called repeatedly in setup mode.

    Parameters:
    duration (float): Delay in seconds between color updates (default: 0.02).
    step_size (float): Amount to advance hue per call (default: 0.002).
    """
    global _fade_led_hue
    import math
    _fade_led_hue = (_fade_led_hue + step_size) % 1.0
    hue = _fade_led_hue
    # HSV to RGB conversion
    def hsv_to_rgb(h: float, s: float = 1.0, v: float = 1.0) -> tuple[int, int, int]:
        """
        Convert HSV color to RGB tuple.
        Returns:
            tuple[int, int, int]: RGB values in 0-255 range.
        """
        i = int(h * 6)
        f = h * 6 - i
        p = int(255 * v * (1 - s))
        q = int(255 * v * (1 - f * s))
        t = int(255 * v * (1 - (1 - f) * s))
        v = int(255 * v)
        i = i % 6
        if i == 0:
            return (v, t, p)
        elif i == 1:
            return (q, v, p)
        elif i == 2:
            return (p, v, t)
        elif i == 3:
            return (p, q, v)
        elif i == 4:
            return (t, p, v)
        elif i == 5:
            return (v, p, q)
        return (0, 0, 0)  # Fallback, should not occur
    rgb = hsv_to_rgb(hue)
    set_color(rgb, 1.0)
    ms = max(1, int(duration * 1000))  # Minimum 1 ms
    utime.sleep_ms(ms)

# Global session state variables
user_active = False
friend_colors = []
start_ts = 0

def save_config(ssid, pw, color):
    with open(CONFIG_FILE, 'w') as f:
        ujson.dump({'ssid':ssid, 'pw':pw, 'color':color}, f)

def load_config():
    with open(CONFIG_FILE) as f:
        return ujson.load(f)

def connect_wifi(ssid, pw, timeout=15):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(ssid, pw)
        for _ in range(timeout):
            if sta.isconnected():
                print("WiFi connected, IP:", sta.ifconfig()[0])
                return True
            utime.sleep(1)
    return sta.isconnected()

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32-Setup')
    print('Started AP, connect to WiFi "ESP32-Setup" and browse to http://192.168.4.1')

def url_decode(s):
    # Basic URL decoding for form data
    # Fallback if 'ure' (MicroPython regex) is missing
    s = s.replace('+', ' ')
    import sys
    try:
        import ure
        s = ure.sub('%([0-9a-fA-F][0-9a-fA-F])', lambda m: chr(int(m.group(1),16)), s)
    except ImportError:
        # Manual percent decoding
        import re
        def pct_decode(match):
            return chr(int(match.group(1), 16))
        s = re.sub(r'%([0-9a-fA-F]{2})', pct_decode, s)
    return s


async def fade_led_task():
    """
    Async task to continuously fade LED through spectrum during config mode.
    """
    while True:
        fade_led_spectrum(duration=0.005, step_size=0.001)
        await asyncio.sleep(0)  # Yield to other tasks

async def captive_portal_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    print('Listening on', addr)
    html_template = load_html_template()
    while True:
        try:
            cl, addr = s.accept()
        except OSError:
            # No connection, yield to event loop
            await asyncio.sleep_ms(10)
            continue
        req = b""
        while True:
            try:
                data = cl.recv(1024)
                if not data: break
                req += data
                if b"\r\n\r\n" in req: break
            except OSError:
                await asyncio.sleep_ms(1)
                continue
        req_str = req.decode()
        if req_str.startswith("GET / "):
            cl.send(b"HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
            cl.sendall(html_template.encode())
        elif req_str.startswith("POST /save"):
            body = req_str.split('\r\n\r\n', 1)[1]
            params = {}
            for pair in body.split('&'):
                k, v = pair.split('=', 1)
                params[k] = url_decode(v)
            ssid = params.get('ssid', '')
            pw = params.get('pw', '')
            color = [int(params.get('r',0)), int(params.get('g',0)), int(params.get('b',0))]
            save_config(ssid, pw, color)
            cl.send(b"HTTP/1.0 200 OK\r\n\r\nSaved! Restarting...")
            cl.close()
            utime.sleep(2)
            machine.reset()
            return
        cl.close()

def serve_captive_portal():
    """
    Start captive portal server and LED fade task concurrently.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(fade_led_task())
    loop.run_until_complete(captive_portal_server())

def try_get_config():
    try:
        config = load_config()
        ok = connect_wifi(config['ssid'], config['pw'])
        if not ok:
            print("WiFi connection failed.")
            raise Exception()
        return config
    except Exception as e:
        print("Need configuration:", e)
        return None

# --------- Main application logic ----------
# LED PWM setup
pwm_r = machine.PWM(machine.Pin(RED_PIN), freq=PWM_FREQ, duty=0)
pwm_g = machine.PWM(machine.Pin(GREEN_PIN), freq=PWM_FREQ, duty=0)
pwm_b = machine.PWM(machine.Pin(BLUE_PIN), freq=PWM_FREQ, duty=0)

def set_color(rgb, brightness):
    # rgb = (r,g,b), brightness 0–1
    for pwm, v in zip((pwm_r, pwm_g, pwm_b), rgb):
        pwm.duty(int(v/255 * brightness * MAX_DUTY))

# Sensor setup

# Initialize I2C bus for VL53L0X sensor
try:
    i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL_PIN), sda=machine.Pin(I2C_SDA_PIN))
    tof = VL53L0X(i2c)
    # Some VL53L0X libraries require a start() call, but most MicroPython ports do not.
    print("VL53L0X sensor initialized.")
except Exception as e:
    print(f"VL53L0X initialization failed: {e}")
    tof = None  # Sensor not available

def color_for_distance(distance_mm: int, min_mm: int = 30, max_mm: int = 300) -> tuple[int, int, int]:
    """
    Map distance in millimeters to an RGB color.
    Closer distances are red, farther are blue, with a gradient in between.

    Parameters:
        distance_mm (int): Distance from TOF sensor in millimeters.
        min_mm (int): Minimum distance for color mapping (default: 30mm).
        max_mm (int): Maximum distance for color mapping (default: 300mm).

    Returns:
        tuple[int, int, int]: RGB color tuple (0-255 per channel).
    """
    # Clamp distance to [min_mm, max_mm]
    d = max(min_mm, min(distance_mm, max_mm))
    # Normalize to [0, 1]
    frac = (d - min_mm) / (max_mm - min_mm)
    # Use HSV: 0=red, 0.66=blue
    import math
    def hsv_to_rgb(h: float, s: float = 1.0, v: float = 1.0) -> tuple[int, int, int]:
        i = int(h * 6)
        f = h * 6 - i
        p = int(255 * v * (1 - s))
        q = int(255 * v * (1 - f * s))
        t = int(255 * v * (1 - (1 - f) * s))
        v = int(255 * v)
        i = i % 6
        if i == 0:
            return (v, t, p)
        elif i == 1:
            return (q, v, p)
        elif i == 2:
            return (p, v, t)
        elif i == 3:
            return (p, q, v)
        elif i == 4:
            return (t, p, v)
        elif i == 5:
            return (v, p, q)
        return (0, 0, 0)
    # Map frac [0,1] to hue [0,0.66] (red to blue)
    hue = 0.0 + frac * 0.66
    return hsv_to_rgb(hue)
user_active = False
friend_colors = []
start_ts = 0


# Try to import urequests, fallback to mrequests, else error
try:
    import urequests
except ImportError:
    try:
        import mrequests as urequests
    except ImportError:
        print("No HTTP request library found. Please add urequests.py or mrequests.py to your project.")
        urequests = None

async def friend_poll_task():
    global friend_colors
    while True:
        if urequests:
            try:
                resp = urequests.get(FRIEND_POLL_URL)
                data = resp.json()
                resp.close()
                cols = []
                for obj in data:
                    c = obj.get("color", {})
                    cols.append((c.get("r",0), c.get("g",0), c.get("b",0)))
                friend_colors = cols
            except Exception as e:
                print(f"Friend poll HTTP error: {e}")
                friend_colors = []
        else:
            print("HTTP request library not available; skipping friend poll.")
            friend_colors = []
        await asyncio.sleep(POLL_INTERVAL)

async def sensor_task(MY_COLOR):
    global user_active, start_ts
    while True:
        # Read distance from VL53L0X sensor using .range property
        d = None
        if tof:
            try:
                d = tof.range
            except Exception as e:
                print(f"VL53L0X read error: {e}")
                d = None
        now = utime.time()
        # Update LED color based on distance
        if d is not None and d > 0:
            rgb = color_for_distance(d)
            set_color(rgb, 1.0)
        else:
            # Sensor unavailable or invalid reading: set LED to dim white
            set_color((128,128,128), 0.2)
        # Session logic
        if d is not None and d > 0 and d <= THRESH_MM:
            if not user_active:
                user_active = True
                start_ts = now
                print("Session started!")
                if urequests:
                    try:
                        urequests.post(START_POST_URL, json={"session":"start"}).close()
                    except Exception as e:
                        print(f"Session start POST error: {e}")
                else:
                    print("HTTP request library not available; cannot POST session start.")
            else:
                start_ts = now
        elif user_active and (now - start_ts) > END_TIMEOUT:
            user_active = False
            print("Session ended!")
        await asyncio.sleep(SENSOR_PERIOD)

async def breath_task(MY_COLOR):
    while True:
        cols = friend_colors.copy()
        if user_active:
            cols.append(MY_COLOR)
        if cols:
            ms = utime.ticks_ms()
            idx = (ms // BREATH_PERIOD_MS) % len(cols)
            frac = (ms % BREATH_PERIOD_MS) / BREATH_PERIOD_MS
            b = (1 - math.cos(2 * math.pi * frac)) / 2
            set_color(cols[idx], b)
            await asyncio.sleep_ms(20)
        else:
            set_color((0,0,0), 0)
            await asyncio.sleep_ms(200)

async def app_main(MY_COLOR):
    await asyncio.gather(
        friend_poll_task(),
        sensor_task(MY_COLOR),
        breath_task(MY_COLOR),
        button_monitor_task()
    )

def run_main_app(config):
    MY_COLOR = tuple(config['color'])
    asyncio.run(app_main(MY_COLOR))



# --------- Startup ---------
if I2C_SCAN_MODE:
    i2c_scan()
elif LASER_DEBUG_MODE:
    # Run laser debug mode loop only
    try:
        asyncio.run(laser_debug_mode_loop())
    except Exception as e:
        print(f"Laser debug mode error: {e}")
else:
    config = try_get_config()
    if not config:
        start_ap()
        serve_captive_portal()
        # Will auto-restart after config is saved.
    else:
        run_main_app(config)
