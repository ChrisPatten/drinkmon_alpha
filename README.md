# Drinkmon Alpha

## Overview
Drinkmon Alpha is an IoT-enabled drink session tracker and social device, featuring:
- ESP32-based hardware for sensor and LED control
- FastAPI backend for session management and friend color sharing
- Captive portal for device WiFi/configuration
- Dockerized backend for easy deployment (ALPHA VERSION!)

## Architecture
- **drinkmon/**: Device logic (hardware, network, config, app state/tasks)
- **drinkmon_server/**: FastAPI backend (session management, API)
- **main.py**: Entrypoint for device logic
- **requirements.txt**: Python dependencies
- **Dockerfile/docker-compose.yml**: Backend deployment

## Features
- Start/end drink sessions
- Share session color with friends via backend
- Sensor-based session detection (VL53L0X distance sensor)
- LED color control and spectrum effects
- Captive portal for WiFi and color setup
- RESTful API for session management

## Quickstart
### Flashing MicroPython to ESP32
1. Connect your ESP32 to your computer via USB.
2. Download the MicroPython firmware (e.g. `ESP32_GENERIC-20250415-v1.25.0.bin`).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Erase the ESP32 flash (optional but recommended):
   ```bash
   esptool.py --chip esp32 erase_flash
   ```
5. Flash MicroPython firmware:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20250415-v1.25.0.bin
   ```
   - Replace `/dev/ttyUSB0` with your ESP32 serial port (e.g. `/dev/cu.usbserial-0001` on macOS). Optionally, omit to try autodetecting the port.
6. After flashing, use a tool like `ampy` (also in requirements) or Thonny to upload the `drinkmon/` directory and `main.py` to the device.
7. On first boot, device starts captive portal for WiFi/color setup.
8. Configure via browser at `http://192.168.4.1`

### Backend (FastAPI)
#### Local
```bash
pip install -r requirements.txt
uvicorn drinkmon_server/drinkmon_api:app --reload
```
#### Docker
```bash
docker-compose -f drinkmon_server/docker-compose.yml up --build
```

## API Endpoints
- `POST /api/start_session` — Start a new session (body: `{color: {r,g,b}}`)
- `POST /api/close_session` — Close session (body: `{guid}`)
- `GET /api/friend_sessions` — List active sessions/colors
- `POST /api/clear_sessions` — Clear all sessions

### Example Models
```json
// Start Session Request
{
  "color": {"r": 135, "g": 206, "b": 235}
}
// Start Session Response
{
  "guid": "..."
}
```

## Configuration
If no configuration is found, the device will start a captive portal to set up WiFi and session color.

Alternatively, you can manually create a `config.json` file with the following structure:
```json
{
  "ssid": "your_wifi_ssid",
  "pw": "your_wifi_password",
  "color": {"r": 255, "g": 0, "b": 0} // RGB color for session
}
```

Use ampy to upload this file to the ESP32:
```bash
ampy --port /dev/ttyUSB0 put config.json
```

## Makefile Commands

The provided Makefile includes useful shortcuts for ESP32 deployment and backend/session management:

| Command         | Description |
|-----------------|-------------|
| `put-drinkmon`  | Uploads the `drinkmon` module to ESP32 using ampy (default port: `/dev/cu.usbserial-0001`). |
| `put-main`      | Uploads `main.py` to ESP32 using ampy. |
| `deploy`        | Uploads both `drinkmon` and `main.py`, then runs `main.py` on ESP32. |
| `session`       | Runs the `start_friend_session.py` script locally to push a random session to the backend. |
| `clear-sessions`| Sends a POST request to clear all sessions on the backend API. |

You can override the default serial port by setting the `PORT` variable:
```bash
make put-main PORT=/dev/ttyUSB0
```

To deploy everything to your ESP32 and start the main app:
```bash
make deploy
```

## Testing
- Backend unit tests: `drinkmon_server/test_drinkmon_api.py`
  - Run with `pytest drinkmon_server/test_drinkmon_api.py`

## Contributing
- Fork and clone the repo
- Use conventional Python style and docstrings
- See `requirements.txt` for dependencies
- PRs and issues welcome!

## License
MIT License (see `drinkmon/hardware/vl53l0x.py` for sensor driver license)

## Credits
- VL53L0X sensor driver by Tony DiCola/Adafruit
- FastAPI, MicroPython, ESP32, and all open-source contributors

---

For questions or support, open an issue or contact the maintainer.
