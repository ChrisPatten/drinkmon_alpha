"""
LED control functions: PWM setup, color setting, fading, spectrum.
Implements set_color, fade_led_spectrum, hsv_to_rgb for extensible LED control.
"""
import machine
import uasyncio as asyncio
import math

RED_PIN, GREEN_PIN, BLUE_PIN = 19, 18, 5
PWM_FREQ, MAX_DUTY = 1000, 1023

pwm_r = machine.PWM(machine.Pin(RED_PIN), freq=PWM_FREQ, duty=0)
pwm_g = machine.PWM(machine.Pin(GREEN_PIN), freq=PWM_FREQ, duty=0)
pwm_b = machine.PWM(machine.Pin(BLUE_PIN), freq=PWM_FREQ, duty=0)

_fade_led_hue = 0.0

def set_color(rgb, brightness):
    """
    Set the LED color using PWM.
    Parameters:
        rgb (tuple): (r, g, b) values 0-255
        brightness (float): 0-1
    """
    for pwm, v in zip((pwm_r, pwm_g, pwm_b), rgb):
        pwm.duty(int(v/255 * brightness * MAX_DUTY))

async def fade_led_spectrum(duration: float = 0.02, step_size: float = 0.002) -> None:
    """
    Fade the LED through the spectrum of colors using PWM.
    This coroutine can be scheduled with uasyncio.create_task.
    """
    global _fade_led_hue
    _fade_led_hue = (_fade_led_hue + step_size) % 1.0
    hue = _fade_led_hue
    rgb = hsv_to_rgb(hue)
    set_color(rgb, 1.0)
    await asyncio.sleep(duration)

def hsv_to_rgb(h: float, s: float = 1.0, v: float = 1.0) -> tuple:
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
