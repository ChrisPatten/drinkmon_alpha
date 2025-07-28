"""
Script to clear all sessions by POSTing to the clear_sessions endpoint.
"""
import requests

API_URL = "https://drinkmon.chrispatten.dev/api/clear_sessions"  # Adjust if server runs elsewhere

def clear_sessions():
    try:
        response = requests.post(API_URL)
        response.raise_for_status()
        print(f"Success: {response.json()}")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_sessions()
