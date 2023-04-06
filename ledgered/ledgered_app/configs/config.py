"""Python module wrapping config.ini for easy access"""
import configparser

config = configparser.ConfigParser()
config.read('/ledgered/ledgered_app/configs/config.ini')

# accessible config values
RESOURCE_PATH = config.get('paths', 'resources')
LOGGER_CONFIG_PATH = config.get('paths', 'logger_config')
