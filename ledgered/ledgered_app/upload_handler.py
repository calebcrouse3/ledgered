from .models import PLUGINS
from .plugins.mint import MintPlugin


def get_plugin_types():
    """Plugins is a list of tuples define in modes, get the first entry of each tuple"""
    return [x[0] for x in PLUGINS]


def handle_upload(file, account_type):
    """Function to process file contents into the data base.
        Should construnct the right plugin, and call the various functions form the plugin.

        File needs to be parsed row by row, 
    """
    plugin_types = get_plugin_types()


    # file is a mint transaction log
    if account_type == "M" and "M" in plugin_types:
        mint = MintPlugin()
        return mint.process(file) # returns dictionary of file processing results


    # file is an amazon transaction log
    elif account_type == "A" and "A" in plugin_types:
        pass
