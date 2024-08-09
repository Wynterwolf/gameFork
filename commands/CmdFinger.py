from evennia import Command as BaseCommand
from evennia.utils.utils import make_iter, justify

class CmdFinger(BaseCommand):
    """
    +finger <player>
    
    Displays detailed information about a player or character with added color.
    """

    key = "+finger"
    locks = "cmd:all()"  # Everyone can use this command
    help_category = "General"

    def func(self):
        "Implement the command"

        if not self.args:
            self.caller.msg("|rUsage:|n +finger <player>")
            return

        target = self.caller.search(self.args.strip())
        if not target:
            return

        # Define the fields you want to display with colors
        fields = [
            ("|wFull Name|n", target.attributes.get("finger_fullname", target.key)),
            ("|cRP Preferences|n", target.attributes.get("finger_rp_preferences", "Not set")),
            ("|mOnline Times|n", target.attributes.get("finger_online_times", "Not set")),
            ("|gUsual Hangouts|n", target.attributes.get("finger_usual_hangouts", "Not set")),
            ("|yRumors|n", target.attributes.get("finger_rumors", "Not set")),
            ("|rIC Job|n", target.attributes.get("finger_ic_job", "Not set")),
        ]

        # Construct the message with colors and add empty lines
        output = []
        output.append("")  # Add an empty line before the content
        for field_name, field_value in fields:
            if field_value != "@@":  # Skip hidden fields
                output.append(f"{field_name}: |w{field_value}|n")
        output.append("")  # Add an empty line after the content

        if len(output) == 2:  # Only empty lines were added
            output.insert(1, "|rNo public information available.|n")

        # Send the constructed message to the caller
        self.caller.msg("\n".join(output))
