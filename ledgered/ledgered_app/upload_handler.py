from .models import PLUGINS
from .plugins.mint import MintPlugin
from .plugins.fidelity import FidelityPlugin
from .plugins.chase import ChasePlugin


def get_plugin_types():
    return [x[0] for x in PLUGINS]


def handle_upload(file, account_type):
    """Pass the uploaded file to the correct plugin.
    The process_file() function returns dictionary of file processing results
    """
    plugin_types = get_plugin_types()

    if account_type == "Mint" and "Mint" in plugin_types:
        mint = MintPlugin()
        return mint.process_file(file)

    if account_type == "Fidelity" and "Fidelity" in plugin_types:
        fidelity = FidelityPlugin()
        return fidelity.process_file(file)

    if account_type == "Chase" and "Chase" in plugin_types:
        chase = ChasePlugin()
        return chase.process_file(file)

    elif account_type == "Amazon" and "Amazon" in plugin_types:
        pass
