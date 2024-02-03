#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_application_segment_browser_access
short_description: Create a Browser Access Application Segment.
description:
  - This module create/update/delete a Browser Access Application Segment in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider

  - zscaler.zpacloud.fragments.state
options:
  id:
    type: str
    description: "Unique ID."
  name:
    type: str
    required: True
    description: "Name of the application."
  description:
    type: str
    required: False
    description: "Description of the application."
  enabled:
    type: bool
    required: False
    description: "Whether this application is enabled or not."
  ip_anchored:
    type: bool
    required: False
    description: "ip_anchored"
  double_encrypt:
    type: bool
    required: False
    description: "Whether Double Encryption is enabled or disabled for the app."
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
    type: str
    required: False
    description: "Indicates whether users can bypass ZPA to access applications."
    choices: ["ALWAYS", "NEVER", "ON_NET"]
  is_cname_enabled:
    type: bool
    required: False
    description: "Indicates if the Zscaler Client Connector (formerly Zscaler App or Z App) receives CNAME DNS records from the connectors."
  health_reporting:
    type: str
    required: False
    description: "Whether health reporting for the app is Continuous or On Access. Supported values: NONE, ON_ACCESS, CONTINUOUS."
    default: "NONE"
    choices: ["NONE", "ON_ACCESS", "CONTINUOUS"]
  server_group_ids:
    type: list
    elements: str
    required: True
    description: "List of the server group IDs."
  segment_group_id:
    type: str
    required: True
    description: "segment group id."
  health_check_type:
    type: str
    description: "health check type."
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
  domain_names:
    type: list
    elements: str
    required: True
    description: "List of domains and IPs."
  clientless_app_ids:
    description: ""
    type: list
    elements: dict
    suboptions:
      path:
        type: str
        required: False
        description: ""
      trust_untrusted_cert:
        type: bool
        required: False
        description: ""
      allow_options:
        type: bool
        required: False
        description: ""
      description:
        type: str
        required: False
        description: ""
      id:
        type: str
        description: ""
      cname:
        type: str
        required: False
        description: ""
      hidden:
        type: bool
        required: False
        description: ""
      app_id:
        type: str
        description: ""
      application_port:
        type: str
        required: False
        description: ""
      application_protocol:
        type: str
        required: True
        description: ""
      name:
        type: str
        required: True
        description: ""
      certificate_id:
        type: str
        required: True
        description: ""
      certificate_name:
        type: str
        required: False
        description: ""
      domain:
        type: str
        required: False
        description: ""
      enabled:
        type: bool
        required: False
        description: ""
      local_domain:
        type: str
        required: False
        description: ""
    required: False
"""

EXAMPLES = """
- name: Create an app segment
  zscaler.zpacloud.zpa_application_segment_browser_access:
    provider: "{{ zpa_cloud }}"
    name: Example Application
    description: Example Application Test
    enabled: true
    health_reporting: ON_ACCESS
    bypass_type: NEVER
    clientless_app_ids:
      - name: "crm.example.com"
        application_protocol: "HTTP"
        application_port: "8080"
        certificate_id: "216196257331282583"
        trust_untrusted_cert: true
        enabled: true
        domain: "crm.example.com"
      - name: "crm2.example.com"
        application_protocol: "HTTP"
        application_port: "8082"
        certificate_id: "216196257331282583"
        trust_untrusted_cert: true
        enabled: true
        domain: "crm.example.com"
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
# The newly created browser access application segment resource record.
"""

# Need to review resource to ensure update occurs successfully.
from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    convert_ports,
    convert_ports_list,
    convert_bool_to_str,
    convert_str_to_bool,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_app_segment_ba(app):
    """
    Normalize application segment pra data by setting computed values.
    """
    normalized = app.copy()

    computed_values = [
        "id",
        "creation_time",
        "modified_by",
        "enabled",
        "config_space",
        "microtenant_name",
        "segment_group_name",
        "server_groups",
        "adp_enabled",
        "app_id",
        "name",
        "ip_anchored",
        "is_incomplete_dr_config",
        "inspect_traffic_with_zia",
        "tcp_port_range",
        "udp_port_range",
        "tcp_port_ranges",
        "udp_port_ranges",
        "description",
        "bypass_type",
        "health_reporting",
        "use_in_dr_mode",
        "clientless_apps",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    if "tcp_keep_alive" in normalized:
        normalized["tcp_keep_alive"] = convert_str_to_bool(normalized["tcp_keep_alive"])

    if "icmp_access_type" in normalized:
        normalized["icmp_access_type"] = normalized["icmp_access_type"] in [
            "PING",
            "PING_TRACEROUTING",
        ]

    if "server_groups" in app:
        normalized["server_group_ids"] = [group["id"] for group in app["server_groups"]]

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    app = dict()
    params = [
        "id",
        "name",
        "enabled",
        "description",
        "bypass_type",
        "clientless_app_ids",
        "domain_names",
        "double_encrypt",
        "health_check_type",
        "health_reporting",
        "ip_anchored",
        "is_cname_enabled",
        "icmp_access_type",
        "select_connector_close_to_app",
        "use_in_dr_mode",
        "is_incomplete_dr_config",
        "inspect_traffic_with_zia",
        "adp_enabled",
        "passive_health_enabled",
        "tcp_port_range",
        "udp_port_range",
        "segment_group_id",
        "server_group_ids",
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

    ba_appsegment_id = module.params.get("id", None)
    ba_appsegment_name = module.params.get("name", None)
    existing_app = None
    if ba_appsegment_id is not None:
        existing_app = client.app_segments.get_segment(segment_id=ba_appsegment_id)
    elif ba_appsegment_name is not None:
        ba_app_segments = client.app_segments.list_segments().to_list()
        for ba_app_segment in ba_app_segments:
            if ba_app_segment.get("name") == ba_appsegment_name:
                existing_app = ba_app_segment
                break

    # Normalize and compare existing and desired application data
    desired_app = normalize_app_segment_ba(app)
    current_app = normalize_app_segment_ba(existing_app) if existing_app else {}

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

    if state == "present":
        if existing_app is not None:
            if differences_detected:
                """Update"""
                existing_app = deleteNone(
                    dict(
                        segment_id=existing_app.get("id"),
                        name=existing_app.get("name", None),
                        description=existing_app.get("description", None),
                        enabled=existing_app.get("enabled", None),
                        bypass_type=existing_app.get("bypass_type", None),
                        clientless_app_ids=existing_app.get("clientless_app_ids", None),
                        domain_names=existing_app.get("domain_names", None),
                        double_encrypt=existing_app.get("double_encrypt", None),
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
                module.warn(
                    "Prepared payload for update_segment: {}".format(existing_app)
                )
                app = client.app_segments.update_segment(**existing_app)
                module.exit_json(changed=True, data=app)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_app)
        else:
            """Create"""
            app = deleteNone(
                dict(
                    name=app.get("name", None),
                    description=app.get("description", None),
                    enabled=app.get("enabled", None),
                    bypass_type=app.get("bypass_type", None),
                    clientless_app_ids=app.get("clientless_app_ids", None),
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
        tcp_keep_alive=dict(type="bool", required=False, default=False),
        icmp_access_type=dict(type="bool", required=False, default=False),
        bypass_type=dict(
            type="str", required=False, choices=["ALWAYS", "NEVER", "ON_NET"]
        ),
        health_reporting=dict(
            type="str",
            required=False,
            default="NONE",
            choices=["NONE", "ON_ACCESS", "CONTINUOUS"],
        ),
        segment_group_id=dict(type="str", required=False),
        double_encrypt=dict(type="bool", required=False),
        health_check_type=dict(type="str"),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", required=False),
        ip_anchored=dict(type="bool", required=False),
        server_group_ids=id_name_spec,
        # server_group_ids=dict(type="list", elements="str", required=False),
        domain_names=dict(type="list", elements="str", required=False),
        tcp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        udp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        clientless_app_ids=dict(
            type="list",
            elements="dict",
            options=dict(
                path=dict(type="str", required=False),
                trust_untrusted_cert=dict(type="bool", required=False),
                allow_options=dict(type="bool", required=False),
                description=dict(type="str", required=False),
                id=dict(type="str"),
                cname=dict(type="str", required=False),
                hidden=dict(type="bool", required=False),
                app_id=dict(type="str"),
                application_port=dict(type="str", required=False),
                application_protocol=dict(type="str", required=True),
                name=dict(type="str", required=True),
                certificate_id=dict(type="str", required=True),
                certificate_name=dict(type="str", required=False),
                domain=dict(type="str", required=False),
                enabled=dict(type="bool", required=False),
                local_domain=dict(type="str", required=False),
            ),
            required=False,
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
