"""Python module wrapping config.ini for easy access"""

import configparser
import os

# sometimes this returns a different folder each time so just hard code for now
PWD = os.getcwd()

config = configparser.ConfigParser()
config.read("config.ini")
config.read(PWD + '/ledgered_app/configs/config.ini')

# accessible config values
RESOURCE_PATH = PWD + config.get('paths', 'resources')
LOGGER_CONFIG_PATH = PWD + config.get('paths', 'logger_config')
