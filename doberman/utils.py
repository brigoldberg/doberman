# utils.py
""" Utility Functions """
import toml


# Read TOML file and return dict
def read_config(fn):
    with open(fn) as fh:
        toml_data = toml.load(fh)
    return toml_data