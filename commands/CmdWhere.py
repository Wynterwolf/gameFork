# commands/CmdWhere.py

from evennia import Command, utils
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import time_format

class CmdWhere(Command):
    """
    Display the locations of all connected players.

    Usage:
      +where

    This command shows the location, name, and idle time of all connected players.
    """
    key = "+where"
    aliases = ["where"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """
        Get the location, name, and idle time of all connected players.
        """
        players = SESSIONS.get_sessions()
        output = []

        for session in players:
            player = session.get_puppet()
            if player:
                location = player.location
                location_name = location.key if location else "Unknown"
                idle_time = time_format(session.cmd_last_visible - session.conn_time, 2)
                output.append(f"{player.name:20} {location_name:30} {idle_time}")

        if output:
            header = f"{'Player':20} {'Location':30} {'Idle'}"
            self.caller.msg(f"{header}\n" + "\n".join(output))
        else:
            self.caller.msg("No players are currently connected.")
