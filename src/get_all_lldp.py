import api_access as api


def _get_engine_service():
    return api.connection.system_service()


def _get_host_interfaces_service(hosts_service, host):
    return hosts_service.host_service(host.id).nics_service()


def _get_all_lldp_info_dictionary():
    all_lldp = {}
    host_service = _get_engine_service().hosts_service()
    for host in host_service.list():
        nics_service = _get_host_interfaces_service(host_service, host)
        host_lldps = {}
        for nic in nics_service.list():
            host_lldps.update({nic.id: _get_lldp_for_nic(nics_service.nic_service(nic.id))})
        all_lldp.update({host.id: host_lldps})
    return all_lldp


def _get_lldp_for_nic(nic_service):
    try:
        return nic_service.link_layer_discovery_protocol_elements_service().list()
    except Exception as ex:
        print ex.message
        return []


if __name__ == "__main__":
    lldps_dict = _get_all_lldp_info_dictionary()
    for id, host_lldps in lldps_dict.items():
        print "-----------------------------------------------------------"
        print "Host: " + id
        print "-----------------------------------------------------------"
        for id, lldp in host_lldps.items():
            print id + " -> " +str(lldp.__len__())
