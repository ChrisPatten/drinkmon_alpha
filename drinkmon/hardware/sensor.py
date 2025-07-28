"""
VL53L0X sensor setup and distance reading.
Implements sensor initialization and get_distance function.
"""
import machine
from drinkmon.hardware.vl53l0x import VL53L0X

I2C_SCL_PIN, I2C_SDA_PIN = 22, 21

try:
    i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL_PIN), sda=machine.Pin(I2C_SDA_PIN))
    tof = VL53L0X(i2c)
except Exception:
    tof = None

def get_distance():
    """
    Read distance from VL53L0X sensor.
    Returns:
        int or None: Distance in mm, or None if error.
    """
    if tof:
        try:
            return tof.range
        except Exception:
            return None
    return None
