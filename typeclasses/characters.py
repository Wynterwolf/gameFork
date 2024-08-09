# typeclasses/characters.py

from evennia import DefaultCharacter
from evennia import default_cmds
from evennia.utils.ansi import ANSIString
from world.wod20th.models import Stat
import re
import random

from commands.CmdFinger import CmdFinger
from commands.CmdSetFingerField import CmdSetFingerField

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        self.add(CmdFinger())
        self.add(CmdSetFingerField())

class Character(DefaultCharacter):
    def get_display_name(self, looker, **kwargs):
        """
        Get the name to display for the character.
        """
        name = self.key
        
        if self.db.gradient_name:
            name = ANSIString(self.db.gradient_name)
            if looker.check_permstring("builders"):
                name += f"({self.dbref})"
            return name
        
        # If the looker is builder+ show the dbref
        if looker.check_permstring("builders"):
            name += f"({self.dbref})"

        return name

    def get_languages(self):
        """
        Get the character's known languages from their merits.
        """
        return_langs = []
        merits = self.db.stats.get('merits', {}).get('social', {})
        for merit in merits:
            if merit.startswith('Language'):
                return_langs.append(merit.split('(')[1].split(')')[0])
        return return_langs

    def set_speaking_language(self, language_name):
        """
        Set the character's currently speaking language.
        """
        if language_name.lower().strip() == "none":
            self.db.speaking_language = None
            return
        # Check if the character knows the language case insensitively.  Lowercasse the language name
        language_name = language_name.lower().strip()
        # use get_languages() to get the list of languages and lowercase them
        languages = [lang.lower() for lang in self.get_languages()]

        if language_name in languages:
            self.db.speaking_language = language_name.capitalize()
        else:
            raise ValueError(f"You don't know the language: {language_name}")

    def get_speaking_language(self):
        """
        Get the character's currently speaking language.
        """
        return self.db.speaking_language

    def detect_tone(self, message):
        """
        Detect the tone of the message based on punctuation and keywords.
        """
        if message.endswith('!'):
            return "excitedly"
        elif message.endswith('?'):
            return "questioningly"
        elif any(word in message.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
            return "in greeting"
        elif any(word in message.lower() for word in ['goodbye', 'bye', 'farewell']):
            return "in farewell"
        elif any(word in message.lower() for word in ['please', 'thank', 'thanks']):
            return "politely"
        elif any(word in message.lower() for word in ['sorry', 'apologize']):
            return "apologetically"
        else:
            return None  # No specific tone detected

    def mask_language(self, message, language):
        """
        Mask the language in the message with more dynamic responses.
        """
        words = len(message.split())
        tone = self.detect_tone(message)

        if words <= 3:
            options = [
                f"<< mutters a few words in {language} >>",
                f"<< something brief in {language} >>",
                f"<< speaks a short {language} phrase >>",
            ]
        elif words <= 10:
            options = [
                f"<< speaks a sentence in {language} >>",
                f"<< a {language} phrase >>",
                f"<< conveys a short message in {language} >>",
            ]
        else:
            options = [
                f"<< gives a lengthy explanation in {language} >>",
                f"<< engages in an extended {language} dialogue >>",
                f"<< speaks at length in {language} >>",
            ]

        masked = random.choice(options)
        
        if tone:
            masked = f"{masked[:-3]}, {tone} >>"

        return masked

    def prepare_say(self, message, language_only=False):
        """
        Prepare the messages for the say command, handling tilde-based language switching.
        """
        use_language = message.lstrip().startswith('~')
        name = self.db.gradient_name if self.db.gradient_name else self.name
        language = self.get_speaking_language()
        
        if use_language:
            # strip the tilde from the message
            message = message[1:].lstrip()
            
            if language and not language_only:
                # Preserve the tilde in the message
                masked_message = self.mask_language(message, language)
                msg_self = f'You say, "{message} |w<< in {language} >>|n"'
                msg_understand = f'{name} says, "{message} |w<< in {language} >>|n"'
                msg_not_understand = f'{name} says, "{masked_message}"'
            else:
                msg_self = f'You say, "{message}"'
                msg_understand = f'{name} says, "{message}"'
                msg_not_understand = msg_understand
               
        else:
            msg_self = f'You say, "{message}"'
            msg_understand = f'{name} says, "{message}"'
            msg_not_understand = msg_understand
        
        if language_only and language:
            msg_self = f'{message} |w<< in {language} >>|n'
            msg_understand = f'{message} |w<< in {language} >>|n'
            msg_not_understand = f'{self.mask_language(message, language)}'    
        elif language_only:
            msg_self = f'{message}'
            msg_understand = f'{message}'
            msg_not_understand = f'{message}'
            language = None
        else:
            language = None

        return msg_self, msg_understand, msg_not_understand, language

    def at_say(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """
        Hook method for the say command. This method is called by the say command,
        but doesn't handle the actual message distribution.
        """
        # This method can be empty or contain any additional logic you want to run when a character speaks
        pass

    def at_pose(self, message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """
        Override the default pose method to use the gradient name, selective language masking, and quote handling.
        """
        if not self.location:
            return

        speaking_language = self.get_speaking_language()
        name = self.db.gradient_name if self.db.gradient_name else self.name
        
        def mask_quotes(match):
            content = match.group(1)
            if content.startswith('~'):
                return f'"{self.mask_language(content[1:], speaking_language)}"'
            return f'"{content}"'

        # Use regex to find and process quoted text
        processed_message = re.sub(r'"(.*?)"', mask_quotes, message)

        if msg_self is None:
            msg_self = f"{name} {message}"  # The poser always understands themselves

        # Create different messages for those who understand and those who don't
        msg_understand = f"{name} {message}"
        msg_not_understand = f"{name} {processed_message}"

        # Send messages to receivers
        for receiver in self.location.contents:
            if receiver != self:
                if speaking_language and speaking_language in receiver.get_languages():
                    receiver.msg(msg_understand)
                else:
                    receiver.msg(msg_not_understand)
            else:
                receiver.msg(msg_self)

    def at_emote(self, emote, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs):
        """
        Override the default emote method to use the gradient name and language masking.
        """
        if not self.location:
            return

        masked_emote = re.sub(r'"([^"]*)"', lambda m: f'"{self.mask_language(m.group(1))}"', emote)

        if msg_self is None:
            msg_self = f"You emote: {masked_emote}"
        if msg_location is None:
            if self.db.gradient_name:
                gradient_name = ANSIString(self.db.gradient_name)
                msg_location = f"{gradient_name} {masked_emote}"
            else:
                msg_location = f"{self.name} {masked_emote}"

        super().at_emote(masked_emote, msg_self=msg_self, msg_location=msg_location, 
                         receivers=receivers, msg_receivers=msg_receivers, **kwargs)

    def get_stat(self, category, stat_type, stat_name, temp=False):
        """
        Retrieve the value of a stat, considering instances if applicable.
        """
        if not hasattr(self.db, "stats") or not self.db.stats:
            self.db.stats = {}

        category_stats = self.db.stats.get(category, {})
        type_stats = category_stats.get(stat_type, {})

        for full_stat_name, stat in type_stats.items():
            # Check if the base stat name matches the given stat_name
            if full_stat_name.startswith(stat_name):
                return stat['temp'] if temp else stat['perm']
        
        stat = Stat.objects.filter(name=stat_name, category=category, stat_type=stat_type).first()
        if stat:
            return stat.default
        return None

    def set_stat(self, category, stat_type, stat_name, value, temp=False):
        """
        Set the value of a stat, considering instances if applicable.
        """
        if not hasattr(self.db, "stats") or not self.db.stats:
            self.db.stats = {}
        if category not in self.db.stats:
            self.db.stats[category] = {}
        if stat_type not in self.db.stats[category]:
            self.db.stats[category][stat_type] = {}
        if stat_name not in self.db.stats[category][stat_type]:
            self.db.stats[category][stat_type][stat_name] = {'perm': 0, 'temp': 0}
        if temp:
            self.db.stats[category][stat_type][stat_name]['temp'] = value
        else:
            self.db.stats[category][stat_type][stat_name]['perm'] = value
            
    def check_stat_value(self, category, stat_type, stat_name, value, temp=False):
        """
        Check if a value is valid for a stat, considering instances if applicable.
        """
        from world.wod20th.models import Stat  
        stat = Stat.objects.filter(name=stat_name, category=category, stat_type=stat_type).first()
        if stat:
            stat_values = stat.values
            return value in stat_values['temp'] if temp else value in stat_values['perm']
        return False

    def colorize_name(self, message):
        """
        Replace instances of the character's name with their gradient name in the message.
        """
        if self.db.gradient_name:
            gradient_name = ANSIString(self.db.gradient_name)
            return message.replace(self.name, str(gradient_name))
        return message

    def at_object_creation(self):
        """
        Called only once, when the object is first created.
        """
        # Set default values for finger attributes
        self.db.finger_fullname = self.key
        self.db.finger_rp_preferences = "Not specified"
        self.db.finger_online_times = "Not specified"
        self.db.finger_usual_hangouts = "Not specified"
        self.db.finger_rumors = "Not specified"
        self.db.finger_ic_job = "Not specified"

    def at_cmdset_get(self, **kwargs):
        """
        This is called when the cmdset is requested from the object.
        """
        self.cmdset.add_default(default_cmds.CharacterCmdSet, permanent=True)
        self.cmdset.add_default(CharacterCmdSet, permanent=True)
