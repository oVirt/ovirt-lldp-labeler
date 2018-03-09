import ConfigParser

_LABELER_CONFIG_FILE = '../etc/ovirt-lldp-labeler.conf'
_CREDENTIALS_CONFIG_FILE = '../etc/ovirt-lldp-credentials.conf'

_CREDENTIALS_SECTION = 'credentials'
_LABELER_SECTION = 'labeler'

_CLUSTER_CONFIG = 'clusters'
_API_URL_CONFIG = 'api_url'

_API_USERNAME = 'username'
_API_PASSWORD = 'password'

_COMMA_SEPARATOR = ','


_config = ConfigParser.ConfigParser()
_config.read(_LABELER_CONFIG_FILE)
_config.read(_CREDENTIALS_CONFIG_FILE)


def get_clusters_from_config():
    return _split_by_separator(_config.get(_LABELER_SECTION, _CLUSTER_CONFIG), _COMMA_SEPARATOR)


def get_api_url():
    return _config.get(_LABELER_SECTION, _API_URL_CONFIG)


def get_api_username():
    return _config.get(_CREDENTIALS_SECTION, _API_USERNAME)


def get_api_password():
    return _config.get(_CREDENTIALS_SECTION, _API_PASSWORD)


def _split_by_separator(value, separator):
    splited = value.split(separator)
    return [val.strip() for val in splited]
