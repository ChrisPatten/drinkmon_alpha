"""
Centralized state management for the drinkmon application.
Encapsulates session, friend, config, and runtime state.
"""

class DrinkmonState:
    def __init__(self):
        self.user_active = False
        self.session_guid = None
        self.start_ts = 0
        self.friend_colors = []
        self.config = None
        self.MY_COLOR = None

    def set_config(self, config):
        self.config = config
        self.MY_COLOR = tuple(config.get('color', (0,0,0)))

    def start_session(self, guid, ts):
        self.user_active = True
        self.session_guid = guid
        self.start_ts = ts

    def end_session(self):
        self.user_active = False
        self.session_guid = None
        self.start_ts = 0

    def update_friend_colors(self, colors):
        self.friend_colors = colors
