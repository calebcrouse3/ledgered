import logging.config

from django.shortcuts import redirect
from ..configs.config import LOGGER_CONFIG_PATH

logging.config.fileConfig(LOGGER_CONFIG_PATH)
logger = logging.getLogger('root')


def save_form(form, owner=None):
    # TODO make one of the parameters a function that get called after validating the form?
    """Validate and save a form and return the saved object. Optionally add a user"""

    if not form.is_valid():
        msg = f"""
        failed to save {type(form)}
        ERRORS: {form.errors.as_data()}
        DATA: {form.data}
        """
        raise Exception(msg)

    obj = form.save(commit=False)
    if owner:
        obj.owner = owner
    obj.save()
    logger.debug(f"successfully saved {type(form)}: {form.data}")
    return obj
