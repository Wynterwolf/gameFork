# commands/CmdSetFingerField.py

from evennia import Command as BaseCommand

class CmdSetFingerField(BaseCommand):
    """
    Sets a custom finger field.

    Usage:
      +setfinger <field_name>=<value>

    Example:
      +setfinger rp_preferences=I prefer detailed roleplay
    """
    key = "+setfinger"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args or "=" not in args:
            caller.msg("Usage: +setfinger <field_name>=<value>")
            return

        field_name, value = [part.strip() for part in args.split("=", 1)]
        # caller.db["finger_" + field_name] = value
        caller.attributes.add("finger_" + field_name, value)
        caller.msg("Set {} to: {}".format(field_name, value))
