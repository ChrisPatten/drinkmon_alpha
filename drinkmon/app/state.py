"""
Centralized state management for the drinkmon application.
Encapsulates session, friend, config, and runtime state.
"""
from typing import Optional, List, Tuple

class DrinkmonState:
    def __init__(self):
        self.user_active: bool = False
        self.session_guid: Optional[str] = None
        self.start_ts: int = 0
        self.friend_colors: List[Tuple[int, int, int]] = []
        self.config: Optional[dict] = None
        self.MY_COLOR: Optional[Tuple[int, int, int]] = None

    def set_config(self, config: dict):
        self.config = config
        self.MY_COLOR = tuple(config.get('color', (0,0,0)))

    def start_session(self, guid: str, ts: int):
        self.user_active = True
        self.session_guid = guid
        self.start_ts = ts

    def end_session(self):
        self.user_active = False
        self.session_guid = None
        self.start_ts = 0

    def update_friend_colors(self, colors: List[Tuple[int, int, int]]):
        self.friend_colors = colors
