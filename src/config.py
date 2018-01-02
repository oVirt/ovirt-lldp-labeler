import ConfigParser
import ast

CONFIG_FILE = '../etc/ovirt-lldp-labeler.conf'
MAIN_SECTION = 'root'
CLUSTER_CONFIG = 'clusters'

_config = ConfigParser.ConfigParser()
_config.read(CONFIG_FILE)


def get_clusters_from_config():
    return ast.literal_eval(_config.get(MAIN_SECTION, CLUSTER_CONFIG))
