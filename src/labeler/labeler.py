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

import config
import logging

from ovirtsdk4.types import NetworkLabel

import api_access as api
import labeler_utils as utils

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


def _update_host_bonds(bonds, attachments, host_id):
    host_service = _get_engine_service().hosts_service().host_service(host_id)
    host_service.setup_networks(modified_bonds=bonds, modified_network_attachments=attachments)
    host_service.commit_net_config()


def _get_lldp_for_host(host_id, with_bonds):
    lldps = {}
    nics_service = _get_host_interfaces_service(host_id)
    nic_list_without_vlan = utils.filter_out_vlan_interfaces(nics_service.list())
    nic_list = utils.filter_out_bond_slaves(nic_list_without_vlan)
    for nic in nic_list:
        if nic.bonding is None:
            lldps.update({nic.id: _get_lldp_for_nic(nics_service, nic)})
        elif with_bonds:
            lldps.update({nic.id: _get_lldp_for_bond_slaves(nics_service, nic)})
    return lldps


def _get_networks_from_attachments(nic_list, attachment_dict):
    networks_service = _get_engine_service().networks_service()
    network_dict = {}
    for nic in nic_list:
        network_attachments = attachment_dict.get(nic, [])
        network_dict.update({nic: [networks_service.network_service(attachment.network.id).get() for attachment
                            in network_attachments]})
    return network_dict


def _create_new_bonds(bond_dict, attachment_dict, host_id, next_bond_num):
    bonds_to_update = []
    attachments_to_update = []
    for aggregation_id, nic_list in bond_dict.items():
        network_dict = _get_networks_from_attachments(nic_list, attachment_dict)
        updated_nic_list = utils.filter_bond_slaves_by_attachments(nic_list, network_dict)
        bond = utils.create_bond_definition(updated_nic_list, next_bond_num)
        attachments = utils.create_attachment_definition(updated_nic_list, next_bond_num, attachment_dict)

        if bond is not None:
            logging.info('Re-attaching networks: %s to bond %s', ', '.join(
                network.name for network in utils.create_network_list(updated_nic_list, network_dict)), bond.name)
            bonds_to_update.append(bond)
            attachments_to_update.extend(attachments)
            next_bond_num += 1

    if len(bonds_to_update) > 0:
        _update_host_bonds(bonds_to_update, attachments_to_update, host_id)


# TODO add diff check for the lldp from slaves
def _get_lldp_for_bond_slaves(nics_service, nic):
    lldp_list = []
    for slave in nic.bonding.slaves:
        nic = nics_service.nic_service(slave.id).get()
        lldp_list.extend(_get_lldp_for_nic(nics_service, nic))
    return lldp_list


def _get_lldp_for_nic(nics_service, nic):
    try:
        nic_service = nics_service.nic_service(nic.id)
        lldp_list = nic_service.link_layer_discovery_protocol_elements_service().list()
        logging.info('Getting lldp information for nic %s', nic.name)
        return lldp_list
    except api.sdk.Error as ex:
        logging.warn(ex.message)
        return []


def _get_nic_label_service(host_id, nic_id):
    return _get_host_interfaces_service(host_id).nic_service(nic_id).network_labels_service()


def _attach_label(host_id, nic, label):
    logging.info('Attaching label %s to nic %s', label, nic.name)
    _get_nic_label_service(host_id, nic.id).add(NetworkLabel(id=label))


def _detach_label(host_id, nic, label):
    logging.info('Detaching label %s from nic %s', label, nic.name)
    _get_nic_label_service(host_id, nic.id).label_service(label).remove()


def _is_label_present_on_host(host_id, label):
    nics = _get_host_interfaces_service(host_id).list()
    for nic in nics:
        attached_labels = [attached_label.id for attached_label in _get_nic_label_service(host_id, nic.id).list()]
        if len(attached_labels) > 0 and label in attached_labels:
            return nic
    return None


def _create_label_candidates_and_assign(host_id, nic, lldps):
    label_candidates = utils.create_label_candidates(utils.filter_vlan_tag(lldps))
    logging.info('Created label candidates for nic %s: %s', nic.name, ', '.join(label_candidates))
    for label_candidate in label_candidates:
        nic_with_label = _is_label_present_on_host(host_id, label_candidate)
        if not (nic_with_label is None or nic_with_label is nic.id):
            _detach_label(host_id, nic_with_label, label_candidate)
            _attach_label(host_id, nic, label_candidate)
        elif nic_with_label is None:
            _attach_label(host_id, nic, label_candidate)


def _get_bond_slave_network_attachments(host_id, nic):
    logging.info('Getting attachments for nic %s', nic.name)
    nics_service = _get_host_interfaces_service(host_id)
    return nics_service.nic_service(nic.id).network_attachments_service().list()


def _run_bond_definition_for_host(host_id):
    nics_service = _get_host_interfaces_service(host_id)
    nic_names = [nic.name for nic in nics_service.list()]
    lldps = _get_lldp_for_host(host_id, with_bonds=False)
    bond_dict = {}
    attachment_dict = {}
    for nic, lldp in lldps.items():
        attachment_dict.update({nic: _get_bond_slave_network_attachments(host_id, nic)})
        utils.update_bond_dict(bond_dict, lldp, nic)
    _create_new_bonds(bond_dict, attachment_dict, host_id, utils.find_next_bond_num(nic_names))


def _run_label_definition_for_host(host_id):
    lldps = _get_lldp_for_host(host_id, with_bonds=True)
    for nic_id, lldp in lldps.items():
        _create_label_candidates_and_assign(host_id, nic_id, lldp)


def run_labeler():
    for host in _get_all_hosts():
        if config.get_auto_bonding():
            logging.info('Running bond definition for host %s', host.name)
            _run_bond_definition_for_host(host.id)
        if config.get_auto_labeling():
            logging.info('Running labeling for host %s', host.name)
            _run_label_definition_for_host(host.id)


def init_labeler(username=None, password=None):
    config_ca_file = config.get_ca_file()
    ca_file = config_ca_file if config_ca_file else None
    username = username if username is not None else config.get_api_username()
    password = password if password is not None else config.get_api_password()
    api.init_connection(config.get_api_url(), username, password, ca_file)


def clear_labeler():
    api.connection.close()
