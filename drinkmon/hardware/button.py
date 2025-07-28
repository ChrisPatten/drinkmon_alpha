"""
Button initialization and monitoring logic.
Implements button setup and async monitoring task.
"""
import machine
import utime as time
import uasyncio as asyncio
from drinkmon.app.session import end_session

BUTTON_PIN = 23
try:
    button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
except Exception:
    button = None

debounce_ms = 200

async def button_monitor_task(state, urequests):
    """
    Monitor the button pin and end session if pressed.
    Calls end_session from session.py for proper deactivation.
    """
    last_press = 0
    while True:
        if button and button.value() == 0:
            now = time.ticks_ms()
            if now - last_press > debounce_ms:
                if state.user_active:
                    end_session(state)
                last_press = now
            await asyncio.sleep_ms(debounce_ms)
        else:
            await asyncio.sleep_ms(20)
