import api_access as api
import lldp_utils as utils


def _get_engine_service():
    return api.connection.system_service()


def _get_host_interfaces_service(hosts_service, hostId):
    return hosts_service.host_service(hostId).nics_service()


def _get_all_lldp_info_dictionary():
    all_lldp = {}
    host_service = _get_engine_service().hosts_service()
    for host in host_service.list():
        nics_service = _get_host_interfaces_service(host_service, host.id)
        host_lldps = {}
        for nic in nics_service.list():
            host_lldps.update({nic.id: _get_lldp_for_nic(nics_service.nic_service(nic.id))})
        all_lldp.update({host.id: host_lldps})
    return all_lldp


def _get_all_lldp_info_dictionary_filtered(lldps_dict):
    filtered_dict = {}
    for hostId, host_lldps in lldps_dict.items():
        filtered_host = {}
        for nicId, tlvs in host_lldps.items():
            filtered_host.update({nicId: utils.filter_vlan_tag(tlvs)})
        filtered_dict.update({hostId: filtered_host})
    return filtered_dict


def _get_lldp_for_nic(nic_service):
    try:
        return nic_service.link_layer_discovery_protocol_elements_service().list()
    except Exception as ex:
        print ex.message
        return []


if __name__ == "__main__":
    lldps_filtered_dict = _get_all_lldp_info_dictionary_filtered(_get_all_lldp_info_dictionary())
    for hostId, host_lldps in lldps_filtered_dict.items():
        print "-----------------------------------------------------------"
        print "Host: " + hostId
        print "-----------------------------------------------------------"
        for nicId, filtered_tlvs in host_lldps.items():
            print "NIC: " + nicId + " -> " + "".join(utils.create_label_candidates(filtered_tlvs))
