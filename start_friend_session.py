"""
Script to manually start a friend session by calling the drinkmon FastAPI backend.
Prompts for color input, calls /api/start_session, and prints the returned GUID.
"""

import requests, random
from typing import Dict

COLORS_DICT = {
    # Primary colors for maximum brightness and clarity on RGB LEDs
    "red": {"r": 255, "g": 0, "b": 0},
    "green": {"r": 0, "g": 255, "b": 0},
    "blue": {"r": 0, "g": 0, "b": 255},

    # Secondary colors (mixes of primaries)
    "yellow": {"r": 255, "g": 255, "b": 0},
    "cyan": {"r": 0, "g": 255, "b": 255},
    "magenta": {"r": 255, "g": 0, "b": 255},

    # Bright and distinct colors for visibility
    "orange": {"r": 255, "g": 128, "b": 0},
    "lime": {"r": 128, "g": 255, "b": 0},
    "pink": {"r": 255, "g": 20, "b": 147},
    "purple": {"r": 128, "g": 0, "b": 128},
    "aqua": {"r": 0, "g": 255, "b": 128},
    "deep_sky_blue": {"r": 0, "g": 191, "b": 255},
    "chartreuse": {"r": 127, "g": 255, "b": 0},
    "spring_green": {"r": 0, "g": 255, "b": 127},
    "violet": {"r": 238, "g": 130, "b": 238},
    "gold": {"r": 255, "g": 215, "b": 0}
}

API_URL = "https://drinkmon.chrispatten.dev/api/start_session"

def get_color_input() -> Dict[str, int]:
    """
    Prompt user for RGB color values and validate input.
    Returns:
        Dict[str, int]: Dictionary with keys 'r', 'g', 'b'.
    """
    def get_channel(name: str) -> int:
        while True:
            try:
                value = int(input(f"Enter {name} (0-255): "))
                if 0 <= value <= 255:
                    return value
                print("Value must be between 0 and 255.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
    return {
        "r": get_channel("red"),
        "g": get_channel("green"),
        "b": get_channel("blue"),
    }

def start_friend_session(color: Dict[str, int]) -> str:
    """
    Call the /api/start_session endpoint to start a friend session.
    Args:
        color (Dict[str, int]): RGB color dictionary.
    Returns:
        str: GUID of the started session.
    Raises:
        Exception: If the API call fails or response is invalid.
    """
    payload = {"color": color}
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        guid = data.get("guid")
        if not guid:
            raise Exception("No GUID returned from API.")
        return guid
    except Exception as e:
        print(f"Error starting session: {e}")
        raise

def main():
    """
    Main function to prompt for color and start a friend session.
    """
    color_key = random.choice(list(COLORS_DICT.keys()))
    print(f"Start a new friend session with color {color_key}:")
    color = COLORS_DICT[color_key]
    try:
        guid = start_friend_session(color)
        print(f"Session started! GUID: {guid}")
    except Exception:
        print("Failed to start session.")

if __name__ == "__main__":
    main()
