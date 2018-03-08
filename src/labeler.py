from __future__ import print_function

from ovirtsdk4.types import NetworkLabel

import api_access as api
import config
import lldp_utils as utils

CLUSTER_QUERY_NAME = 'cluster'


def _get_engine_service():
    return api.connection.system_service()


def _get_all_hosts(filtered_by_cluster=True):
    filter_query = ''
    if filtered_by_cluster:
        filter_query = utils.get_or_query(CLUSTER_QUERY_NAME, config.get_clusters_from_config())

    return _get_engine_service().hosts_service().list(search=filter_query)


def _get_host_interfaces_service(host_id):
    return _get_engine_service().hosts_service().host_service(host_id).nics_service()


def _get_lldp_for_host(host_id):
    lldps = {}
    nics_service = _get_host_interfaces_service(host_id)
    for nic in nics_service.list():
        lldps.update({nic.id: _get_lldp_for_nic(nics_service.nic_service(nic.id))})
    return lldps


def _get_lldp_for_nic(nic_service, vlan_only=True):
    try:
        lldp_list = nic_service.link_layer_discovery_protocol_elements_service().list()
        if vlan_only:
            lldp_list = utils.filter_vlan_tag(lldp_list)
        return lldp_list
    except api.sdk.Error as ex:
        print(ex.message)
        return []


def _get_nic_label_service(host_id, nic_id):
    return _get_host_interfaces_service(host_id).nic_service(nic_id).network_labels_service()


def _attach_label(host_id, nic_id, label):
    _get_nic_label_service(host_id, nic_id).add(NetworkLabel(id=label))


def _detach_label(host_id, nic_id, label):
    _get_nic_label_service(host_id, nic_id).label_service(label).remove()


def _is_label_present_on_host(host_id, label):
    nics = _get_host_interfaces_service(host_id).list()
    for nic in nics:
        attached_labels = [attached_label.id for attached_label in _get_nic_label_service(host_id, nic.id).list()]
        if attached_labels.__len__() > 0 and label in attached_labels:
            return nic.id
    return None


def _create_label_candidates_and_assign(host_id, nic_id, lldps):
    label_candidates = utils.create_label_candidates(lldps)
    for label_candidate in label_candidates:
        nic_with_label = _is_label_present_on_host(host_id, label_candidate)
        if not (nic_with_label is None or nic_with_label is nic_id):
            _detach_label(host_id, nic_with_label, label_candidate)
            _attach_label(host_id, nic_id, label_candidate)
        elif nic_with_label is None:
            _attach_label(host_id, nic_id, label_candidate)


def run_labeler():
    for host in _get_all_hosts():
        lldps = _get_lldp_for_host(host.id)
        for nic_id, lldp in lldps.items():
            _create_label_candidates_and_assign(host.id, nic_id, lldp)


def init_labeler():
    api.init_connection(config.get_api_url(), config.get_api_username(), config.get_api_password())


if __name__ == "__main__":
    init_labeler()
    run_labeler()
