import itertools

PORT_VLAN_TYPE = 127
PORT_VLAN_OUI = 0x0080c2
PORT_VLAN_SUBTYPE = 1

LABEL_PREFIX = "lldp_vlan_"


def filter_vlan_tag(tlvs):
    filtered_tlvs = []
    for tlv in tlvs:
        if tlv.type == PORT_VLAN_TYPE and tlv.oui == PORT_VLAN_OUI and tlv.subtype == PORT_VLAN_SUBTYPE:
            filtered_tlvs.append(tlv.properties)
    return _flat_map(filtered_tlvs)


def _flat_map(tlvs_property_list):
    return list(itertools.chain.from_iterable(tlvs_property_list))


def create_label_candidates(tlv_properties):
    label_candidates = []
    for property in tlv_properties:
        label_candidates.append(LABEL_PREFIX + property.value)
    return label_candidates
