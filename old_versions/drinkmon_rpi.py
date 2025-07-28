import RPi.GPIO as GPIO
import time
import random

# HC-SR04 pins
TRIG = 22
ECHO = 27

# 74HC595 pins
REG_DATA = 21
REG_LATCH = 20
REG_CLOCK = 16


END_SESSION_TIMEOUT = 10 # seconds
SENSOR_DISTANCE = 10 # CM
LOOP_FREQUENCY = 1.0 # seconds
VERBOSE = True

led_states = {
    LED_BLUE: False,
    LED_YELLOW: False,
    LED_GREEN: False,
    LED_RED: False
}

def init_shift_register():
    """Initialize the 74HC595 shift register pins."""
    GPIO.setmode(GPIO.BCM)
    for pin in [REG_DATA, REG_LATCH, REG_CLOCK]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def set_leds(target_led_values):
    """
    Set the state of the LEDs using the 74HC595 shift register.
    Q0 -> LED_BLUE
    Q1 -> LED_YELLOW
    Q2 -> LED_GREEN
    Q3 -> LED_RED
    """
    # Build the byte to send to the shift register
    value = (int(target_led_values[LED_BLUE]) << 0) | \
            (int(target_led_values[LED_YELLOW]) << 1) | \
            (int(target_led_values[LED_GREEN]) << 2) | \
            (int(target_led_values[LED_RED]) << 3)
    
    # Latch low
    GPIO.output(REG_LATCH, GPIO.LOW)
    
    # Shift out the bits, LSB first
    for i in range(8):
        bit = (value >> i) & 1
        GPIO.output(REG_DATA, GPIO.HIGH if bit else GPIO.LOW)
        GPIO.output(REG_CLOCK, GPIO.HIGH)
        GPIO.output(REG_CLOCK, GPIO.LOW)

    # Latch high to apply the new state
    GPIO.output(REG_LATCH, GPIO.HIGH)


def get_distance_cm():
    # send 10µs pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start, pulse_end = 0, 0

    # wait for echo start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    # wait for echo end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    try:
        pulse_duration = pulse_end - pulse_start
    except UnboundLocalError:
        pulse_duration = -1
    # sound speed ~34300 cm/s, round-trip
    distance = pulse_duration * 17150
    return distance

def poll_for_update():
    if random.randint(1, 10) < 5:
        return True
    else:
        return False

def send_start_session():
    print('Bottle picked up!')

def send_end_session():
    print("We're done!")


if __name__ == "__main__":
    # ensure trigger is low
    GPIO.output(TRIG, False)
    set_leds(led_states)
    time.sleep(2)

    print('GPIO Configured')

    try:
        target_led = False
        start_time = 0
        active_session = False
        loop_counter = 0

        while True:

            if loop_counter == 9:
                if poll_for_update():
                    print('Toggle friend session')
                    led_states[LED_GREEN] = (led_states[LED_GREEN] == False)
                loop_counter = 0
            else:
                loop_counter = loop_counter + 1

            dist = get_distance_cm()

            if dist < 0: # Bad distance reading, try again
                time.sleep(LOOP_FREQUENCY)
                continue

            bottle_presence = (dist <= SENSOR_DISTANCE)
            curr_time = int(time.time())
            session_time = curr_time - start_time

            if VERBOSE:
                print(f'bottle_presence: {bottle_presence} | active_session: {active_session} | session_time: {session_time}')

            if not bottle_presence and not active_session: # Start a session
                start_time = curr_time
                active_session = True
                send_start_session()
                led_states[PRIMARY_LED] = True
            elif active_session and not bottle_presence: # Restart the session
                start_time = curr_time
            elif active_session and session_time > END_SESSION_TIMEOUT: # End a session
                send_end_session()
                active_session = False
                led_states[PRIMARY_LED] = False
                
            set_leds(led_states)

            time.sleep(LOOP_FREQUENCY)

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()