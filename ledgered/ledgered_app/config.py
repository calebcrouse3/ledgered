import configparser
import os

config = configparser.ConfigParser()
config.read('./ledgered_app/config.ini')

RESOURCE_PATH = os.getcwd() + config.get('paths', 'resources')

