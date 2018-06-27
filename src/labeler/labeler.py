# Copyright 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
from __future__ import print_function

import config

from ovirtsdk4.types import NetworkLabel

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


def _get_host_interfaces_service(host_id):
    return _get_engine_service().hosts_service().host_service(host_id).nics_service()


def _get_lldp_for_host(host_id):
    lldps = {}
    nics_service = _get_host_interfaces_service(host_id)
    nic_list_without_vlan = _filter_out_vlan_interfaces(nics_service.list())
    nic_list = _filter_out_bond_slaves(nic_list_without_vlan)
    for nic in nic_list:
        if nic.bonding is None:
            lldps.update({nic.id: _get_lldp_for_nic(nics_service, nic)})
        else:
            lldps.update({nic.id: _get_lldp_for_bond_slaves(nics_service, nic)})
    return lldps


# TODO add diff check for the lldp from slaves
def _get_lldp_for_bond_slaves(nics_service, nic):
    lldp_list = []
    for slave in nic.bonding:
        lldp_list.append(_get_lldp_for_nic(nics_service.nic_service(slave.id)))
    return utils.flat_map(lldp_list)


def _filter_out_vlan_interfaces(nic_list):
    return [nic for nic in nic_list if nic.vlan is None]


def _filter_out_bond_slaves(nic_list):
    slaves_list = []
    for nic in nic_list:
        if nic.bonding is not None:
            slaves_list.append([slave.id for slave in nic.bonding.slaves])
    flat_slave_list = utils.flat_map(slaves_list)
    return [nic for nic in nic_list if nic.id not in flat_slave_list]


def _get_lldp_for_nic(nics_service, nic, vlan_only=True):
    try:
        nic_service = nics_service.nic_service(nic.id)
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
        if len(attached_labels) > 0 and label in attached_labels:
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


def init_labeler(username=None, password=None):
    config_ca_file = config.get_ca_file()
    ca_file = config_ca_file if config_ca_file else None
    username = username if username is not None else config.get_api_username()
    password = password if password is not None else config.get_api_password()
    api.init_connection(config.get_api_url(), username, password, ca_file)


def clear_labeler():
    api.connection.close()
