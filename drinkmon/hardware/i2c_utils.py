"""
I2C scanning and related utilities.
Implements i2c_scan for hardware debugging.
"""
import machine

I2C_SCL_PIN, I2C_SDA_PIN = 22, 21

def i2c_scan(i2c=None):
    """
    Scan the I2C bus and print all detected device addresses.
    """
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
