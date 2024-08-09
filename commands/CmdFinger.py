from evennia import Command as BaseCommand

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

        # Iterate over all attributes that start with 'finger_'
        finger_data = target.attributes.all()
        output = []
        output.append("|C========================================|n")  # Add a separator line

        for attr in finger_data:
            attr_name, attr_value = attr.key, attr.value
            if attr_name.startswith("finger_"):
                field_name = attr_name[7:].replace("_", " ").capitalize()  # Strip 'finger_' and format
                output.append(f"|g{field_name}|n: |y{attr_value}|n")

        if len(output) == 1:  # No attributes were found
            output.append("|rNo public information available.|n")

        output.append("|C========================================|n")  # Add a separator line

        # Send the constructed message to the caller
        self.caller.msg("\n".join(output))
