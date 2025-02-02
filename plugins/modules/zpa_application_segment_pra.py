#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>

#                             MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_application_segment_pra
short_description: Create an PRA application segment in the ZPA Cloud.
description:
    - This module will create/update/delete an Privileged Remote Access application segment
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

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
    description:
      - List of tcp port range pairs, e.g. [22, 22] for port 22-22, [80, 100] for 80-100.
    required: false
    suboptions:
      from:
        type: str
        required: false
        description:
          - List of valid TCP ports. The application segment API supports multiple TCP and UDP port ranges.
      to:
        type: str
        required: false
        description:
          - List of valid TCP ports. The application segment API supports multiple TCP and UDP port ranges.
  udp_port_range:
    type: list
    elements: dict
    description:
      - List of udp port range pairs, e.g. ['35000', '35000'] for port 35000.
    required: false
    suboptions:
      from:
        type: str
        required: false
        description:
          - List of valid UDP ports. The application segment API supports multiple TCP and UDP port ranges.
      to:
        type: str
        required: false
        description:
          - List of valid UDP ports. The application segment API supports multiple TCP and UDP port ranges.
  tcp_port_ranges:
    description:
      - The list of TCP port ranges used to access the application
    type: list
    elements: str
    required: false
  udp_port_ranges:
    description:
      - The list of UDP port ranges used to access the application
    type: list
    elements: str
    required: false
  common_apps_dto:
    type: dict
    required: true
    description: "Configuration of common applications, e.g., inspection or Browser Access."
    suboptions:
      apps_config:
        type: list
        elements: dict
        required: true
        description: "Detailed configuration for each application."
        suboptions:
          name:
            description: "The name of the application."
            type: str
            required: true
          description:
            description: "The description of the application."
            type: str
            required: false
          enabled:
            description: "Whether the application is enabled."
            type: bool
            required: false
          app_types:
            description: "This denotes the operation type."
            type: list
            elements: str
            required: true
            choices: ["BROWSER_ACCESS", "SIPA", "INSPECT", "SECURE_REMOTE_ACCESS"]
          application_port:
            description: "Port for the application."
            type: str
            required: true
          application_protocol:
            description: "Protocol for the application."
            type: str
            required: true
            choices: ["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET", "VNC", "NONE"]
          connection_security:
            description: "The security type of the connection."
            type: str
            required: false
            choices: ["ANY", "NLA", "NLA_EXT", "TLS", "VM_CONNECT", "RDP"]
          domain:
            description: "The domain of the application."
            type: str
            required: true
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
  tcp_keep_alive:
    description:
      - Indicates whether TCP communication sockets are enabled or disabled.
    type: bool
    required: false
  select_connector_close_to_app:
    description:
      - Whether the App Connector is closest to the application (True) or closest to the user (False).
    type: bool
    required: false
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
    elements: str
    required: true
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
    required: false
"""

EXAMPLES = """
- name: Create an Application Segment PRA
  zscaler.zpacloud.zpa_application_segment_pra:
    provider: "{{ zpa_cloud }}"
    name: Ansible_Application_Segment_PRA
    description: Ansible_Application_Segment_PRA
    enabled: true
    is_cname_enabled: true
    tcp_keep_alive: true
    passive_health_enabled: true
    select_connector_close_to_app: false
    health_check_type: "DEFAULT"
    health_reporting: "ON_ACCESS"
    bypass_type: "NEVER"
    icmp_access_type: false
    tcp_port_range:
      - from: "22"
        to: "22"
      - from: "3389"
        to: "3389"
    domain_names:
      - ssh_pra.example.com
      - rdp_pra.example.com
    segment_group_id: "216196257331368720"
    server_group_ids:
      - "216196257331368722"
    common_apps_dto:
      apps_config:
        - name: "ssh_pra"
          description: "Description for common app"
          domain: ssh_pra.example.com
          application_port: "22"
          application_protocol: "SSH"
          enabled: true
          app_types:
            - "SECURE_REMOTE_ACCESS"
        - name: "rdp_pra"
          description: "Description for common app"
          domain: rdp_pra.example.com
          application_port: "3389"
          application_protocol: "RDP"
          connection_security: "ANY"
          enabled: true
          app_types:
            - "SECURE_REMOTE_ACCESS"
"""

RETURN = """
# The newly created privileged remote access application segment resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    convert_ports,
    convert_ports_list,
    convert_bool_to_str,
    convert_str_to_bool,
    normalize_common_apps,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_app_segment_pra(app):
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
        "app_id",
        "name",
        "ip_anchored",
        "is_incomplete_dr_config",
        "inspect_traffic_with_zia",
        "tcp_port_range",
        "udp_port_range",
        "description",
        "bypass_type",
        "health_reporting",
        "use_in_dr_mode",
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

    if "common_apps_dto" in normalized and normalized["common_apps_dto"]:
        normalized["common_apps_dto"] = normalize_common_apps(
            normalized["common_apps_dto"]
        )
    return normalized


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
        "ip_anchored",
        "icmp_access_type",
        "common_apps_dto",
        "segment_group_id",
        "server_group_ids",
        "domain_names",
    ]
    for param_name in params:
        app[param_name] = module.params.get(param_name)

    common_apps_dto = module.params.get("common_apps_dto")
    if common_apps_dto:
        app["common_apps_dto"] = (
            common_apps_dto  # Ensuring the key is set in the dictionary
        )

    # For debugging purposes: Print the app dictionary before API calls
    # module.warn("Final Payload before API call: {app}")

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

    segment_id = module.params.get("id", None)
    appsegment_name = module.params.get("name", None)
    existing_app = None
    if segment_id is not None:
        existing_app = client.app_segments_pra.get_segment_pra(segment_id=segment_id)
    elif appsegment_name is not None:
        ba_app_segments = client.app_segments_pra.list_segments_pra().to_list()
        for ba_app_segment in ba_app_segments:
            if ba_app_segment.get("name") == appsegment_name:
                existing_app = ba_app_segment
                break

    # Normalize and compare existing and desired application data
    desired_app = normalize_app_segment_pra(app)
    current_app = normalize_app_segment_pra(existing_app) if existing_app else {}

    fields_to_exclude = ["id"]
    differences_detected = False

    for key, desired_value in desired_app.items():
        if key in fields_to_exclude:
            continue

        current_value = current_app.get(key)

        if key == "domain_names":
            # Compare them as sorted lists to ignore order differences
            if sorted(current_value or []) != sorted(desired_value or []):
                differences_detected = True
                module.warn(
                    f"Difference detected in domain_names. "
                    f"Current (sorted): {sorted(current_value or [])}, "
                    f"Desired (sorted): {sorted(desired_value or [])}"
                )
        else:
            # Normal comparison for everything else
            if current_value != desired_value:
                differences_detected = True
                module.warn(
                    f"Difference detected in {key}. "
                    f"Current: {current_value}, Desired: {desired_value}"
                )
                # module.warn(
                #     f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {desired_value}"
                # )

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_app is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_app is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

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
                        common_apps_dto=existing_app.get(
                            "common_apps_dto", None
                        ),  # Add this line
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
                existing_app = client.app_segments_pra.update_segment_pra(
                    **existing_app
                )
                module.exit_json(changed=True, data=existing_app)
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
                    common_apps_dto=app.get("common_apps_dto", None),  # Add this line
                    is_incomplete_dr_config=app.get("is_incomplete_dr_config", None),
                    inspect_traffic_with_zia=app.get("inspect_traffic_with_zia", None),
                    segment_group_id=app.get("segment_group_id", None),
                    server_group_ids=app.get("server_group_ids", None),
                    tcp_port_ranges=convert_ports_list(app.get("tcp_port_range", None)),
                    udp_port_ranges=convert_ports_list(app.get("udp_port_range", None)),
                )
            )
            app = client.app_segments_pra.add_segment_pra(**app)
            module.exit_json(changed=True, data=app)
    elif (
        state == "absent"
        and existing_app is not None
        and existing_app.get("id") is not None
    ):
        code = client.app_segments_pra.delete_segment_pra(
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
        required=True,
    )
    apps_config_spec = dict(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        app_types=dict(
            type="list",
            elements="str",
            choices=["BROWSER_ACCESS", "SIPA", "INSPECT", "SECURE_REMOTE_ACCESS"],
            required=True,
        ),
        application_port=dict(type="str", required=True),
        application_protocol=dict(
            type="str",
            choices=["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET", "VNC", "NONE"],
            required=True,
        ),
        connection_security=dict(
            type="str",
            choices=["ANY", "NLA", "NLA_EXT", "TLS", "VM_CONNECT", "RDP"],
            required=False,
        ),
        domain=dict(type="str", required=True),
    )
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        select_connector_close_to_app=dict(type="bool", required=False),
        use_in_dr_mode=dict(type="bool", required=False),
        is_incomplete_dr_config=dict(type="bool", required=False),
        inspect_traffic_with_zia=dict(type="bool", required=False),
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
        tcp_keep_alive=dict(type="bool", required=False),
        segment_group_id=dict(type="str", required=True),
        double_encrypt=dict(type="bool", required=False),
        health_check_type=dict(type="str"),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", required=False),
        ip_anchored=dict(type="bool", required=False),
        icmp_access_type=dict(type="bool", required=False),
        id=dict(type="str", required=False),
        server_group_ids=id_name_spec,
        domain_names=dict(type="list", elements="str", required=False),
        common_apps_dto=dict(
            type="dict",
            options={
                "apps_config": dict(
                    type="list",
                    elements="dict",
                    options=apps_config_spec,
                    required=True,
                ),
            },
            required=True,
        ),
        tcp_port_ranges=dict(type="list", elements="str", required=False),
        udp_port_ranges=dict(type="list", elements="str", required=False),
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
