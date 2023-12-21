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
module: zpa_application_segment
short_description: Create an application segment in the ZPA Cloud.
description:
    - This module will create/update/delete an application segment
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
    - zscaler.zpacloud.fragments.enabled_state
options:
  id:
    description:
      - ID of the application.
    required: false
    type: str
  name:
    description:
      - Name of the application.
    required: true
    type: str
  description:
    description:
      - Description of the application.
    required: false
    type: str
  enabled:
    description:
      - Whether this application is enabled or not.
    type: bool
    required: false
  ip_anchored:
    description:
      - Whether Source IP Anchoring for use with ZIA, is enabled or disabled for the app.
    type: bool
    required: false
  tcp_port_range:
    type: list
    elements: dict
    required: False
    description: "The TCP port ranges used to access the application"
    suboptions:
      from:
        type: str
        required: False
        description: "The starting port for a port range"
      to:
        type: str
        required: False
        description: "The ending port for a port range"
  udp_port_range:
    type: list
    elements: dict
    required: False
    description: "The UDP port ranges used to access the application"
    suboptions:
      from:
        type: str
        required: False
        description: "The starting port for a port range"
      to:
        type: str
        required: False
        description: "The ending port for a port range"
  double_encrypt:
    description:
      - Whether Double Encryption is enabled or disabled for the app.
    type: bool
    required: false
  icmp_access_type:
    description:
      - Indicates the ICMP access type.
    type: bool
    required: false
    default: false
  tcp_keep_alive:
    description:
      - Indicates whether TCP communication sockets are enabled or disabled.
    type: bool
    required: false
    default: false
  select_connector_close_to_app:
    description:
      - Whether the App Connector is closest to the application (True) or closest to the user (False).
    type: bool
    required: false
    default: false
  passive_health_enabled:
    description:
      - passive health enabled.
    type: bool
    required: false
  use_in_dr_mode:
    description: "Whether or not the application resource is designated for disaster recovery"
    type: bool
    required: false
  is_incomplete_dr_config:
    description: "Indicates whether or not the disaster recovery configuration is incomplete"
    type: bool
    required: false
  inspect_traffic_with_zia:
    description:
      - Indicates if Inspect Traffic with ZIA is enabled for the application
      - When enabled, this leverages a single posture for securing internet/SaaS and private applications
      - and applies Data Loss Prevention policies to the application segment you are creating
    type: bool
    required: false
  adp_enabled:
    description:
      - Indicates if Active Directory Inspection is enabled or not for the application
      - This allows the application segment's traffic to be inspected by Active Directory (AD) Protection
      - By default, this field is set to false
    type: bool
    required: false
  bypass_type:
    description:
      - Indicates whether users can bypass ZPA to access applications.
    type: str
    required: false
    choices:
      - ALWAYS
      - NEVER
      - ON_NET
    default: NEVER
  is_cname_enabled:
    description:
      - Indicates if the Zscaler Client Connector (formerly Zscaler App or Z App) receives CNAME DNS records from the connectors.
    type: bool
    required: false
  health_reporting:
    description:
      - Whether health reporting for the app is Continuous or On Access. Supported values are NONE, ON_ACCESS, CONTINUOUS
    type: str
    required: false
    choices:
      - NONE
      - ON_ACCESS
      - CONTINUOUS
    default: NONE
  server_group_ids:
    description:
      - ID of the server group.
    type: list
    elements: dict
    required: true
    suboptions:
      name:
        required: false
        type: str
        description: ""
      id:
        required: true
        type: str
        description: ""
  segment_group_id:
    description:
      - ID of the segment group.
    type: str
    required: true
  health_check_type:
    description:
      - health check type.
    type: str
    required: false
  domain_names:
    description:
      - List of domains and IPs.
    type: list
    elements: str
    required: true
"""

EXAMPLES = """
- name: Create/Update/Delete an application segment.
  zscaler.zpacloud.zpa_application_segment:
    provider: "{{ zpa_cloud }}"
    name: Example Application Segment
    description: Example Application Segment
    enabled: true
    health_reporting: ON_ACCESS
    bypass_type: NEVER
    is_cname_enabled: true
    tcp_port_range:
      - from: "80"
        to: "80"
    domain_names:
      - crm.example.com
    segment_group_id: "216196257331291896"
    server_group_ids:
      - "216196257331291969"
"""

RETURN = """
# The newly created application segment resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    convert_ports_list,
    convert_ports,
    convert_bool_to_str,
    normalize_app,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    app = dict()
    params = [
        "id",
        "name",
        "description",
        "tcp_port_range",
        "udp_port_range",
        "enabled",
        "bypass_type",
        "health_reporting",
        "double_encrypt",
        "tcp_keep_alive",
        "health_check_type",
        "is_cname_enabled",
        "passive_health_enabled",
        "select_connector_close_to_app",
        "use_in_dr_mode",
        "is_incomplete_dr_config",
        "inspect_traffic_with_zia",
        "adp_enabled",
        "ip_anchored",
        "icmp_access_type",
        "segment_group_id",
        "server_group_ids",
        "domain_names",
    ]
    for param_name in params:
        app[param_name] = module.params.get(param_name)

    # Usage for tcp_keep_alive
    tcp_keep_alive = module.params.get("tcp_keep_alive")
    converted_tcp_keep_alive = convert_bool_to_str(
        tcp_keep_alive, true_value="1", false_value="0"
    )
    app["tcp_keep_alive"] = converted_tcp_keep_alive

    # Get icmp_access_type
    icmp_access_type = module.params.get("icmp_access_type")

    # Convert icmp_access_type
    if isinstance(icmp_access_type, bool):
        app["icmp_access_type"] = "PING" if icmp_access_type else "NONE"
    else:
        # You might want to fail the module here since you only want to allow boolean values
        module.fail_json(
            msg="Invalid value for icmp_access_type: {}. Only boolean values are allowed.".format(
                icmp_access_type
            )
        )

    select_connector_close_to_app = module.params.get(
        "select_connector_close_to_app", None
    )
    udp_port_range = module.params.get("udp_port_range", None)

    if select_connector_close_to_app and udp_port_range is not None:
        module.fail_json(
            msg="Invalid configuration: 'select_connector_close_to_app' cannot be set to True when 'udp_port_range' is defined."
        )

    appsegment_id = module.params.get("id", None)
    appsegment_name = module.params.get("name", None)
    existing_app = None
    if appsegment_id is not None:
        existing_app = client.app_segments.get_segment(segment_id=appsegment_id)
    elif appsegment_name is not None:
        ba_app_segments = client.app_segments.list_segments().to_list()
        for ba_app_segment in ba_app_segments:
            if ba_app_segment.get("name") == appsegment_name:
                existing_app = ba_app_segment
                break
    # Normalize and compare existing and desired application data
    desired_app = normalize_app(app)
    current_app = normalize_app(existing_app) if existing_app else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_app.items():
        if key not in fields_to_exclude and current_app.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {value}"
            )

    if existing_app is not None:
        id = existing_app.get("id")
        existing_app.update(app)
        existing_app["id"] = id

    module.warn(f"Final payload being sent to SDK: {app}")
    if state == "present":
        if existing_app is not None:
            if differences_detected:
                """Update"""
                existing_app = deleteNone(
                    dict(
                        segment_id=existing_app.get("id"),
                        bypass_type=existing_app.get("bypass_type", None),
                        description=existing_app.get("description", None),
                        domain_names=existing_app.get("domain_names", None),
                        double_encrypt=existing_app.get("double_encrypt", None),
                        enabled=existing_app.get("enabled", None),
                        health_check_type=existing_app.get("health_check_type", None),
                        health_reporting=existing_app.get("health_reporting", None),
                        ip_anchored=existing_app.get("ip_anchored", None),
                        is_cname_enabled=existing_app.get("is_cname_enabled", None),
                        tcp_keep_alive=existing_app.get("tcp_keep_alive", None),
                        icmp_access_type=existing_app.get("icmp_access_type", None),
                        select_connector_close_to_app=existing_app.get(
                            "select_connector_close_to_app", None
                        ),
                        use_in_dr_mode=existing_app.get("use_in_dr_mode", None),
                        is_incomplete_dr_config=existing_app.get(
                            "is_incomplete_dr_config", None
                        ),
                        inspect_traffic_with_zia=existing_app.get(
                            "inspect_traffic_with_zia", None
                        ),
                        adp_enabled=existing_app.get("adp_enabled", None),
                        name=existing_app.get("name", None),
                        passive_health_enabled=existing_app.get(
                            "passive_health_enabled", None
                        ),
                        segment_group_id=existing_app.get("segment_group_id", None),
                        server_group_ids=existing_app.get("server_group_ids", None),
                        tcp_port_ranges=convert_ports(
                            existing_app.get("tcp_port_range", None)
                        ),
                        udp_port_ranges=convert_ports(
                            existing_app.get("udp_port_range", None)
                        ),
                    )
                )
                module.warn("Payload Update for SDK: {}".format(existing_app))
                existing_app = client.app_segments.update_segment(
                    **existing_app
                ).to_dict()
                module.exit_json(changed=True, data=existing_app)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_app)
        else:
            module.warn("Creating new rule as no existing rule found")
            """Create"""
            app = deleteNone(
                dict(
                    name=app.get("name", None),
                    description=app.get("description", None),
                    enabled=app.get("enabled", None),
                    bypass_type=app.get("bypass_type", None),
                    domain_names=app.get("domain_names", None),
                    double_encrypt=app.get("double_encrypt", None),
                    health_check_type=app.get("health_check_type", None),
                    health_reporting=app.get("health_reporting", None),
                    ip_anchored=app.get("ip_anchored", None),
                    is_cname_enabled=app.get("is_cname_enabled", None),
                    tcp_keep_alive=app.get("tcp_keep_alive", None),
                    icmp_access_type=app.get("icmp_access_type", None),
                    passive_health_enabled=app.get("passive_health_enabled", None),
                    select_connector_close_to_app=app.get(
                        "select_connector_close_to_app", None
                    ),
                    use_in_dr_mode=app.get("use_in_dr_mode", None),
                    is_incomplete_dr_config=app.get("is_incomplete_dr_config", None),
                    inspect_traffic_with_zia=app.get("inspect_traffic_with_zia", None),
                    adp_enabled=app.get("adp_enabled", None),
                    segment_group_id=app.get("segment_group_id", None),
                    server_group_ids=app.get("server_group_ids", None),
                    tcp_port_ranges=convert_ports_list(app.get("tcp_port_range", None)),
                    udp_port_ranges=convert_ports_list(app.get("udp_port_range", None)),
                )
            )
            module.warn("Payload for SDK: {}".format(app))
            app = client.app_segments.add_segment(**app)
            module.exit_json(changed=True, data=app)
    elif (
        state == "absent"
        and existing_app is not None
        and existing_app.get("id") is not None
    ):
        code = client.app_segments.delete_segment(
            segment_id=existing_app.get("id"), force_delete=True
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_app)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    port_spec = dict(to=dict(type="str", required=False))
    port_spec["from"] = dict(type="str", required=False)
    id_name_spec = dict(
        type="list",
        elements="str",
        required=False,
    )
    argument_spec.update(
        id=dict(type="str"),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        select_connector_close_to_app=dict(type="bool", required=False),
        use_in_dr_mode=dict(type="bool", required=False),
        is_incomplete_dr_config=dict(type="bool", required=False),
        inspect_traffic_with_zia=dict(type="bool", required=False),
        adp_enabled=dict(type="bool", required=False),
        bypass_type=dict(
            type="str",
            required=False,
            default="NEVER",
            choices=["ALWAYS", "NEVER", "ON_NET"],
        ),
        health_reporting=dict(
            type="str",
            required=False,
            default="NONE",
            choices=["NONE", "ON_ACCESS", "CONTINUOUS"],
        ),
        tcp_keep_alive=dict(type="bool", required=False, default=False),
        segment_group_id=dict(type="str", required=False),
        double_encrypt=dict(type="bool", required=False),
        health_check_type=dict(type="str"),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", required=False),
        ip_anchored=dict(type="bool", required=False),
        icmp_access_type=dict(type="bool", required=False, default=False),
        server_group_ids=id_name_spec,
        domain_names=dict(type="list", elements="str", required=False),
        tcp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        udp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
