#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_app_connector_groups
short_description: Create an App Connector Group in the ZPA Cloud.
description:
  - This module creates/update/delete an App Connector Group in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
options:
  client_id:
    description: ""
    required: false
    type: str
  client_secret:
    description: ""
    required: false
    type: str
  customer_id:
    description: ""
    required: false
    type: str
  name:
    description:
      - Name of the App Connector Group.
    required: true
    type: str
  description:
    description: ""
    required: false
    type: str
  city_country:
    description:
        - City Country of the App Connector Group.
    type: str
  country_code:
    description:
      - Country code of the App Connector Group.
    type: str
  dns_query_type:
    description:
      - Whether to enable IPv4 or IPv6, or both, for DNS resolution of all applications in the App Connector Group.
    type: str
    choices:
        - IPV4_IPV6
        - IPV4
        - IPV6
    default: IPV4_IPV6
  enabled:
    description:
      - Whether this App Connector Group is enabled or not.
    type: bool
    default: true
  pra_enabled:
    description:
      - Whether or not privileged remote access is enabled for the App Connector Group.
    type: bool
    default: false
  waf_disabled:
    description:
      - Whether or not AppProtection is disabled for the App Connector Group.
    type: bool
    default: false
  latitude:
    description:
      - Latitude of the App Connector Group. Integer or decimal. With values in the range of -90 to 90.
    required: false
    type: str
  location:
    description:
      - Location of the App Connector Group.
    required: false
    type: str
  longitude:
    description:
      - Longitude of the App Connector Group. Integer or decimal. With values in the range of -180 to 180.
    required: false
    type: str
  lss_app_connector_group:
    description:
      - LSS app connector group
    required: false
    type: str
  upgrade_day:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified day.
      - List of valid days (i.e., Sunday, Monday).
    default: SUNDAY
    type: str
  upgrade_time_in_secs:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    default: '66600'
    type: str
  override_version_profile:
    description:
      - App Connectors in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    required: false
    type: bool
    default: false
  version_profile_id:
    description:
      - ID of the version profile. To learn more, see Version Profile Use Cases.
      - This value is required, if the value for overrideVersionProfile is set to true.
    required: false
    type: str
    default: '0'
    choices:
      - '0'
      - '1'
      - '2'
  version_profile_name:
    description:
      - Name of the version profile.
    required: false
    type: str
  state:
    description:
      - Whether the app connector group should be present or absent.
    type: str
    choices:
        - present
        - absent
    default: present
"""

EXAMPLES = """
- name: Create/Update/Delete an App Connector Group
  zscaler.zpacloud.zpa_app_connector_groups:
    name: "Example"
    description: "Example2"
    enabled: true
    city_country: "California, US"
    country_code: "US"
    latitude: "37.3382082"
    longitude: "-121.8863286"
    location: "San Jose, CA, USA"
    upgrade_day: "SUNDAY"
    upgrade_time_in_secs: "66600"
    override_version_profile: true
    version_profile_id: "0"
    dns_query_type: "IPV4"
"""

RETURN = """
# The newly created app connector group resource record.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    deleteNone,
    ZPAClientHelper,
)

def validate_latitude(val):
    try:
        v = float(val)
        if v < -90 or v > 90:
            return (None, ["latitude must be between -90 and 90"])
    except ValueError:
        return (None, ["latitude value should be a valid float number"])
    return (None, None)

def validate_longitude(val):
    try:
        v = float(val)
        if v < -180 or v > 180:
            return (None, ["longitude must be between -180 and 180"])
    except ValueError:
        return (None, ["longitude value should be a valid float number"])
    return (None, None)

def diff_suppress_func_coordinate(old, new):
    try:
        o = round(float(old) * 1000000) / 1000000
        n = round(float(new) * 1000000) / 1000000
        return o == n
    except ValueError:
        return False

def validate_tcp_quick_ack(tcp_quick_ack_app, tcp_quick_ack_assistant, tcp_quick_ack_read_assistant):
    if tcp_quick_ack_app != tcp_quick_ack_assistant or \
       tcp_quick_ack_app != tcp_quick_ack_read_assistant or \
       tcp_quick_ack_assistant != tcp_quick_ack_read_assistant:
        return "the values of tcpQuickAck related flags need to be consistent"
    return None

def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    group = dict()

    latitude = module.params.get('latitude')
    longitude = module.params.get('longitude')
    _, lat_errors = validate_latitude(latitude)
    _, lon_errors = validate_longitude(longitude)

    if lat_errors or lon_errors:
        all_errors = lat_errors + lon_errors
        module.fail_json(msg=", ".join(all_errors))

    # Validate the TCP Quick Ack attributes
    tcp_quick_ack_app = module.params['tcp_quick_ack_app']
    tcp_quick_ack_assistant = module.params['tcp_quick_ack_assistant']
    tcp_quick_ack_read_assistant = module.params['tcp_quick_ack_read_assistant']

    tcp_quick_ack_error = validate_tcp_quick_ack(tcp_quick_ack_app, tcp_quick_ack_assistant, tcp_quick_ack_read_assistant)
    if tcp_quick_ack_error:
        module.fail_json(msg=tcp_quick_ack_error)

    group = dict()
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "city_country",
        "country_code",
        "latitude",
        "longitude",
        "location",
        "upgrade_day",
        "upgrade_time_in_secs",
        "override_version_profile",
        "version_profile_id",
        "version_profile_name",
        "dns_query_type",
        "lss_app_connector_group",
        "tcp_quick_ack_app",
        "tcp_quick_ack_assistant",
        "tcp_quick_ack_read_assistant",
        "use_in_dr_mode",
        "pra_enabled",
        "waf_disabled",
    ]
    for param_name in params:
        group[param_name] = module.params.get(param_name, None)
    group_id = group.get("id", None)
    group_name = group.get("name", None)
    existing_group = None
    if group_id is not None:
        group_box = client.connector_groups.get_connector_group(group_id=group_id)
        if group_box is not None:
            existing_group = group_box.to_dict()
    elif group_name is not None:
        groups = client.connector_groups.list_connector_groups().to_list()
        for group_ in groups:
            if group_.get("name") == group_name:
                existing_group = group_
    if existing_group is not None:
        id = existing_group.get("id")
        existing_group.update(group)
        existing_group["id"] = id
    if state == "present":
        if existing_group is not None:
            """Update"""
            # Check if latitude and longitude need to be updated
            existing_lat = existing_group.get("latitude")
            new_lat = group.get("latitude")
            if diff_suppress_func_coordinate(existing_lat, new_lat):
                existing_group["latitude"] = existing_lat  # reset to original if they're deemed equal

            existing_long = existing_group.get("longitude")
            new_long = group.get("longitude")
            if diff_suppress_func_coordinate(existing_long, new_long):
                existing_group["longitude"] = existing_long  # reset to original if they're deemed equal

            existing_group = deleteNone(
                dict(
                    group_id=existing_group.get("id"),
                    name=existing_group.get("name"),
                    description=existing_group.get("description"),
                    enabled=existing_group.get("enabled"),
                    city_country=existing_group.get("city_country"),
                    country_code=existing_group.get("country_code"),
                    latitude=existing_group.get("latitude"),
                    longitude=existing_group.get("longitude"),
                    location=existing_group.get("location"),
                    upgrade_day=existing_group.get("upgrade_day"),
                    upgrade_time_in_secs=existing_group.get("upgrade_time_in_secs"),
                    override_version_profile=existing_group.get("override_version_profile"),
                    version_profile_id=existing_group.get("version_profile_id"),
                    version_profile_name=existing_group.get("version_profile_name"),
                    dns_query_type=existing_group.get("dns_query_type"),
                    tcp_quick_ack_app=existing_group.get("tcp_quick_ack_app"),
                    tcp_quick_ack_assistant=existing_group.get("tcp_quick_ack_assistant"),
                    tcp_quick_ack_read_assistant=existing_group.get("tcp_quick_ack_read_assistant"),
                    use_in_dr_mode=existing_group.get("use_in_dr_mode"),
                    pra_enabled=existing_group.get("pra_enabled"),
                    waf_disabled=existing_group.get("waf_disabled"),
                )
            )
            existing_group = client.connectors.update_connector_group(
                **existing_group
            ).to_dict()
            module.exit_json(changed=True, data=existing_group)
        else:
            """Create"""
            group = deleteNone(
                dict(
                    name=group.get("name"),
                    description=group.get("description"),
                    enabled=group.get("enabled"),
                    city_country=group.get("city_country"),
                    country_code=group.get("country_code"),
                    latitude=group.get("latitude"),
                    longitude=group.get("longitude"),
                    location=group.get("location"),
                    upgrade_day=group.get("upgrade_day"),
                    upgrade_time_in_secs=group.get("upgrade_time_in_secs"),
                    override_version_profile=group.get("override_version_profile"),
                    version_profile_id=group.get("version_profile_id"),
                    version_profile_name=group.get("version_profile_name"),
                    dns_query_type=group.get("dns_query_type"),
                    tcp_quick_ack_app=group.get("tcp_quick_ack_app"),
                    tcp_quick_ack_assistant=group.get("tcp_quick_ack_assistant"),
                    tcp_quick_ack_read_assistant=group.get("tcp_quick_ack_read_assistant"),
                    use_in_dr_mode=group.get("use_in_dr_mode"),
                    pra_enabled=group.get("pra_enabled"),
                    waf_disabled=group.get("waf_disabled"),
                )
            )
            group = client.connectors.add_connector_group(**group).to_dict()
            module.exit_json(changed=True, data=group)
    elif state == "absent":
        if existing_group is not None and existing_group.get("id") is not None:
            code = client.connectors.delete_connector_group(
                group_id=existing_group.get("id")
            )
            if code > 299:
                module.exit_json(changed=False, data=None)
            module.exit_json(changed=True, data=existing_group)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    id_name_spec = dict(
        type="list",
        elements="dict",
        options=dict(
            id=dict(type="str", required=False), name=dict(type="str", required=False)
        ),
        required=False,
    )
    argument_spec.update(
        connectors=id_name_spec,
        name=dict(type="str", required=True),
        id=dict(type="str", required=False),
        city_country=dict(type="str", required=False),
        country_code=dict(type="str", required=False),
        description=dict(type="str", required=False),
        dns_query_type=dict(
            type="str",
            choices=["IPV4_IPV6", "IPV4", "IPV6"],
            required=False,
            default="IPV4_IPV6",
        ),
        enabled=dict(type="bool", default=True, required=False),
        latitude=dict(type="str", required=False),
        location=dict(type="str", required=False),
        longitude=dict(type="str", required=False),
        lss_app_connector_group=dict(type="str", required=False),
        upgrade_day=dict(type="str", default="SUNDAY", choices=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"], required=False),
        upgrade_time_in_secs=dict(type="str", default=66600, required=False),
        override_version_profile=dict(type="bool", default=False, required=False),
        version_profile_id=dict(
            type="str", default="0", choices=["0", "1", "2"], required=False
        ),
        version_profile_name=dict(type="str", choices=["Default", "Previous Default", "New Release"], required=False),
        tcp_quick_ack_app=dict(type="bool", default=False, required=False),
        tcp_quick_ack_assistant=dict(type="bool", default=False, required=False),
        tcp_quick_ack_read_assistant=dict(type="bool", default=False, required=False),
        use_in_dr_mode=dict(type="bool", default=False, required=False),
        pra_enabled=dict(type="bool", default=False, required=False),
        waf_disabled=dict(type="bool", default=False, required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
