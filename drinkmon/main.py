"""
Entry point for the application. Handles startup logic, mode selection, and coordinates modules.
Implements main startup logic and mode selection using DrinkmonState and session.py endpoint methods.
"""
from drinkmon.hardware.i2c_utils import i2c_scan
from drinkmon.hardware.led import fade_led_spectrum
from drinkmon.network.wifi import connect_wifi, start_ap
from drinkmon.network.captive_portal import captive_portal_server
from drinkmon.config.config_manager import load_config, save_config, url_decode
from drinkmon.app.tasks import app_main
from drinkmon.app.state import DrinkmonState
import uasyncio as asyncio

I2C_SCAN_MODE = False

state = DrinkmonState()

def try_get_config():
    try:
        config = load_config()
        ok = connect_wifi(config['ssid'], config['pw'])
        if not ok:
            print("WiFi connection failed.")
            raise Exception()
        state.set_config(config)
        return config
    except Exception as e:
        print("Need configuration:", e)
        return None

def serve_captive_portal():
    loop = asyncio.get_event_loop()
    loop.create_task(fade_led_spectrum())
    loop.run_until_complete(captive_portal_server())

def run_main_app():
    asyncio.run(app_main(state))

if __name__ == "__main__":
    if I2C_SCAN_MODE:
        i2c_scan()
    else:
        config = try_get_config()
        if not config:
            start_ap()
            serve_captive_portal()
        else:
            run_main_app()
