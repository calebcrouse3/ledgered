"""Python module wrapping config.ini for easy access"""

import configparser
import os

PWD = os.getcwd()

config = configparser.ConfigParser()
config.read(PWD + '/ledgered/ledgered_app/configs/config.ini')

# accessible config values
RESOURCE_PATH = PWD + config.get('paths', 'resources')
LOGGER_CONFIG_PATH = PWD + config.get('paths', 'logger_config')
