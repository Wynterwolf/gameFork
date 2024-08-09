# /home/wynterwolf/eveTestThree/game/commands/CmdWeather.py

import requests
import xml.etree.ElementTree as ET
from evennia import Command
from datetime import datetime
from dateutil import parser
import pytz
from evennia.utils import ansi
from evennia.utils import utils

class CmdWeather(Command):
    """
    Command to check the weather.
    Usage:
      +weather

    Displays the current weather.
    """
    key = "weather"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        city_id = "5391811"  # Replace with your city ID
        appid = "b515d74fb581cf045182c2c9a37427cd"  # Replace with your API key
        url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&mode=xml&appid={appid}"

        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.content
            temperature, sunrise, sunset = self.parse_weather_data(weather_data)
            temperature_f = self.kelvin_to_fahrenheit(temperature)

            # Add ANSI colors using escape sequences
            message = (
                f"\033[36mCurrent Temperature:\033[0m \033[33m{temperature_f:.2f} F\033[0m\n"
                f"\033[36mSunrise:\033[0m \033[32m{sunrise}\033[0m\n"
                f"\033[36mSunset:\033[0m \033[31m{sunset}\033[0m"
            )
            self.caller.msg(message)
        else:
            self.caller.msg("\033[31mFailed to retrieve weather information.\033[0m")

    # Other methods remain the same...

    def parse_weather_data(self, xml_data):
        root = ET.fromstring(xml_data)
        temperature = float(root.find('temperature').attrib['value'])
        sunrise = root.find('city/sun').attrib['rise']
        sunset = root.find('city/sun').attrib['set']
        sunrise = self.format_time(sunrise)
        sunset = self.format_time(sunset)
        return temperature, sunrise, sunset

    def format_time(self, time_str):
        # Use dateutil.parser to parse the ISO 8601 string
        time_obj = parser.isoparse(time_str)
        # Convert time from UTC to local timezone
        local_timezone = pytz.timezone('America/Chicago')  # Replace 'YOUR_TIMEZONE' with your local timezone, e.g., 'America/Los_Angeles'
        local_time = time_obj.astimezone(local_timezone)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    def kelvin_to_fahrenheit(self, kelvin):
        celsius = kelvin - 273.15
        fahrenheit = (celsius * 9/5) + 32
        return fahrenheit