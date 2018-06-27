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
import itertools

PORT_VLAN_TYPE = 127
PORT_VLAN_OUI = 0x0080c2
PORT_VLAN_SUBTYPE = 3
PROPERTY_VLAN_NAME = "VLAN ID"

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
        if property.name == PROPERTY_VLAN_NAME:
            label_candidates.append(LABEL_PREFIX + property.value)
    return label_candidates


def get_or_query(param, values):
    return ' OR '.join(['{}={}'.format(param, val) for val in values])
