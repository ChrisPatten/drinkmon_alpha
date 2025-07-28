"""
Async tasks for sensor, breath, button, friend polling, and main app orchestration.
Implements async tasks for main app logic using DrinkmonState and session.py endpoint methods.
"""
import uasyncio as asyncio
import utime as time
import math
from drinkmon.hardware.led import set_color, hsv_to_rgb
from drinkmon.hardware.sensor import get_distance
from drinkmon.app.session import start_session, end_session, friend_poll
from drinkmon.app.session import get_start_session_url, get_end_session_url, get_friend_poll_url
from drinkmon.app.state import DrinkmonState

END_TIMEOUT = 60
THRESH_MM = 100
SENSOR_PERIOD = 1.0
BREATH_PERIOD_MS = 2000
POLL_INTERVAL = 30

async def friend_poll_task(state: DrinkmonState):
    while True:
        friend_poll(state)
        await asyncio.sleep(POLL_INTERVAL)

async def sensor_task(state: DrinkmonState):
    while True:
        d = get_distance()
        now = time.time()
        if state.user_active:
            set_color(state.MY_COLOR, 1.0)
        else:
            set_color((0,0,0), 0)
        if d is not None and d > THRESH_MM:
            if not state.user_active:
                guid = start_session(state, state.MY_COLOR, now)
                if guid:
                    state.start_ts = now
            else:
                state.start_ts = now
        elif state.user_active and (now - state.start_ts) > END_TIMEOUT:
            end_session(state)
        await asyncio.sleep(SENSOR_PERIOD)

async def breath_task(state: DrinkmonState):
    while True:
        cols = state.friend_colors.copy()
        if cols:
            ms = time.ticks_ms()
            idx = (ms // BREATH_PERIOD_MS) % len(cols)
            frac = (ms % BREATH_PERIOD_MS) / BREATH_PERIOD_MS
            b = (1 - math.cos(2 * math.pi * frac)) / 2
            set_color(cols[idx], b)
            await asyncio.sleep_ms(20)
        else:
            set_color((0,0,0), 0)
            await asyncio.sleep_ms(200)

async def app_main(state: DrinkmonState):
    await asyncio.gather(
        friend_poll_task(state),
        sensor_task(state),
        breath_task(state)
    )
