import ConfigParser
from distutils.util import strtobool

CONFIG_FILE = '../etc/ovirt-lldp-labeler.conf'
MAIN_SECTION = 'root'
CLUSTER_CONFIG = 'clusters'
IGNORE_COLLISION_CONFIG = 'ignore_collision'
COMMA_SEPARATOR = ','

_config = ConfigParser.ConfigParser()
_config.read(CONFIG_FILE)


def get_clusters_from_config():
    return _split_by_separator(_config.get(MAIN_SECTION, CLUSTER_CONFIG), COMMA_SEPARATOR)


def _split_by_separator(value, separator):
    splited = value.split(separator)
    return [val.strip() for val in splited]


def get_is_collison_ignored():
    try:
        return strtobool(_config.get(MAIN_SECTION, IGNORE_COLLISION_CONFIG))
    except ValueError:
        return True
