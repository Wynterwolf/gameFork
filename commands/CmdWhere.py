from evennia import Command
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import ansi

class CmdWhere(Command):
    """
    +where

    Displays the current locations of all online players.
    Usage:
      +where
    """
    key = "+where"
    aliases = ["where"]
    locks = "cmd:all()"

    def func(self):
        """Implement the +where command"""

        # Get a list of all connected sessions
        sessions = SESSIONS.get_sessions()
        if not sessions:
            self.caller.msg("No players found.")
            return

        # Build the output
        header = "|w{:<20}{:<30}{:<40}|n".format("Player", "Location", "Area")
        separator = "|C" + "-"*90 + "|n"
        output = [header, separator]

        for session in sessions:
            player = session.account  # Access the Account/Player object
            char = session.puppet  # Access the Character object
            if char and char.location:
                location_name = char.location.key
                area_name = char.location.db.area_name if char.location.db.area_name else "Unknown Area"
                output.append("{:<20}{:<30}{:<40}".format(char.key, location_name, area_name))
            else:
                output.append("{:<20}{:<30}{:<40}".format(player.key if player else 'Unknown', "Unknown Location", "Unknown Area"))

        # Send the result back to the caller
        self.caller.msg("\n".join(output))
