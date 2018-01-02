from __future__ import print_function

import config
import api_access as api
import lldp_utils as utils

CLUSTER_QUERY_NAME = 'cluster'


def _get_engine_service():
    return api.connection.system_service()


def _get_all_hosts(filtered_by_cluster=True):
    filter_query = ''
    if filtered_by_cluster:
        filter_query = utils.get_or_query(CLUSTER_QUERY_NAME, config.get_clusters_from_config())

    return _get_engine_service().hosts_service().list(search=filter_query)


def _get_host_interfaces_service(hosts_service, host_id):
    return hosts_service.host_service(host_id).nics_service()


def _get_lldp_for_host(host_id):
    host_service = _get_engine_service().hosts_service()
    lldps = {}
    nics_service = _get_host_interfaces_service(host_service, host_id)
    for nic in nics_service.list():
        lldps.update({nic.id: _get_lldp_for_nic(nics_service.nic_service(nic.id))})
    return lldps


def _get_lldp_for_nic(nic_service, vlan_only=True):
    try:
        lldp_list = nic_service.link_layer_discovery_protocol_elements_service().list()
        if vlan_only:
            lldp_list = utils.filter_vlan_tag(lldp_list)
        return lldp_list
    except Exception as ex:
        print(ex.message)
        return []


if __name__ == "__main__":
    for host in _get_all_hosts():
        lldps = _get_lldp_for_host(host.id)
        for nic_id, lldp in lldps.items():
            print(nic_id + ': ' + lldp)
