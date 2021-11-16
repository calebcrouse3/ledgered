from .models import PLUGINS
from .plugins.mint import MintPlugin

def handle_upload(file, account_type):
    """Function to process file contents into the data base.
        Should construnct the right plugin, and call the various functions form the plugin.

        File needs to be parsed row by row, 
    """
    plugin_types = [x[0] for x in PLUGINS]

    # file is a mint transaction log
    if account_type == "M" and "M" in plugin_types:
        mint = MintPlugin()
        return mint.process_pandas(file) # returns the number of new entries

    # file is an amazon transaction log
    elif account_type == "A" and "A" in plugin_types:
        pass
