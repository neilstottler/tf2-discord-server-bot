# Std Lib Imports
pass

# 3rd Party Imports
import yaml
from dotted_dict import DottedDict

# Local Imports


def load_config():
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.Loader)
    return DottedDict(config)