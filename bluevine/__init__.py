import os
import json

import logging

logger = logging.getLogger(__file__)


def load_config():
    """ loads the configuration json file to a dictionary """

    config_path = os.environ["TRELLO_MANAGER_CONFIG_PATH"]
    try:
        config_file = open(config_path, 'r')
        return json.load(config_file)
    except IOError as e:
        logger.error("Couldn't read the configuration file")
        raise
    except ValueError as e:
        logger.error("Invlaid json format in configuration file")
        raise


app_config = load_config()
