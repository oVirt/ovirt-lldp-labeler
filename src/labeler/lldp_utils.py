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
    return flat_map(filtered_tlvs)


def flat_map(list_to_flat_map):
    return list(itertools.chain.from_iterable(list_to_flat_map))


def create_label_candidates(tlv_properties):
    label_candidates = []
    for property in tlv_properties:
        label_candidates.append(LABEL_PREFIX + property.value)
    return label_candidates


def get_or_query(param, values):
    return ' OR '.join(['{}={}'.format(param, val) for val in values])
