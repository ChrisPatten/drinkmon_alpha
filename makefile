# Default serial port for ESP32
PORT ?= /dev/cu.usbserial-0001

# Upload the drinkmon module to ESP32 using ampy
put-drinkmon:
	.venv/bin/ampy --port $(PORT) put drinkmon

# Upload main.py to ESP32 using ampy
put-main:
	.venv/bin/ampy --port $(PORT) put main.py

deploy: put-drinkmon put-main
	.venv/bin/ampy --port $(PORT) run -n main.py

session:
	.venv/bin/python -m start_friend_session.py

clear-sessions:
	curl -X POST https://drinkmon.chrispatten.dev/api/clear_sessions