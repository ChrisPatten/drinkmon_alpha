"""
Session state management, start/end session logic, GUID handling, and API endpoint management.
"""
from drinkmon.app.state import DrinkmonState

# HTTP client import with fallback
try:
    import urequests as requests
except ImportError:
    try:
        import mrequests as requests
    except ImportError:
        requests = None
        print("No HTTP request library found. Please add urequests.py or mrequests.py to your project.")

BASE_URL = "https://drinkmon.chrispatten.dev/api"

def get_start_session_url() -> str:
    return f"{BASE_URL}/start_session"

def get_end_session_url() -> str:
    return f"{BASE_URL}/end_session"

def get_friend_poll_url() -> str:
    return f"{BASE_URL}/friend_sessions"

def start_session(state: DrinkmonState, MY_COLOR, ts):
    """
    Start a session by POSTing to the server.
    Updates state if successful.
    """
    url = get_start_session_url()
    if requests:
        try:
            payload = {"color": {"r": MY_COLOR[0], "g": MY_COLOR[1], "b": MY_COLOR[2]}}
            resp = requests.post(url, json=payload)
            if resp.status_code == 200:
                resp_json = resp.json()
                guid = resp_json.get("guid")
                resp.close()
                state.start_session(guid, ts)
                return guid
            resp.close()
        except Exception as e:
            print(f"Session start POST error: {e}")
    return None

def end_session(state: DrinkmonState):
    """
    End a session by POSTing to the server and updating state.
    """
    url = get_end_session_url()
    if state.session_guid and requests:
        try:
            payload = {"guid": state.session_guid}
            resp = requests.post(url, json=payload)
            resp.close()
        except Exception as e:
            print(f"Session close POST error: {e}")
    state.end_session()

def friend_poll(state: DrinkmonState):
    """
    Poll the friend session API and update state.friend_colors.
    Returns an empty list if polling fails or no data is available.
    """
    url = get_friend_poll_url()
    if not requests:
        print("HTTP request library not available; cannot poll friend sessions.")
        state.update_friend_colors([])
        return []
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            resp.close()
            cols = []
            for obj in data:
                c = obj.get("color", {})
                cols.append((c.get("r",0), c.get("g",0), c.get("b",0)))
            state.update_friend_colors(cols)
            return cols
        else:
            print(f"Friend poll HTTP error: {resp.status_code}")
            resp.close()
            state.update_friend_colors([])
            return []
    except Exception as e:
        print(f"Friend poll HTTP error: {e}")
        state.update_friend_colors([])
        return []
