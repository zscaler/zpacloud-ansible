#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
  default_max_age:
    type: str
    required: False
    default: ""
    description: "default_max_age"
  ip_anchored:
    type: bool
    required: False
    description: "ip_anchored"
  udp_port_range:
    type: list
    elements: dict
    required: False
    description: "udp port range"
    suboptions:
      to:
        type: str
        required: False
        description: ""
      from:
        type: str
        required: False
        description: ""
  id:
    type: str
    description: "Unique ID."
  double_encrypt:
    type: bool
    required: False
    description: "Whether Double Encryption is enabled or disabled for the app."
  icmp_access_type:
    type: str
    required: False
    default: "NONE"
    choices: ["PING_TRACEROUTING", "PING", "NONE"]
    description: "icmp access type."
  default_idle_timeout:
    type: str
    required: False
    default: ""
    description: "default idle timeout."
  passive_health_enabled:
    type: bool
    required: False
    description: "passive health enabled."
  bypass_type:
    type: str
    required: False
    description: "Indicates whether users can bypass ZPA to access applications."
    choices: ["ALWAYS", "NEVER", "ON_NET"]
  is_cname_enabled:
    type: bool
    required: False
    description: "Indicates if the Zscaler Client Connector (formerly Zscaler App or Z App) receives CNAME DNS records from the connectors."
  name:
    type: str
    required: True
    description: "Name of the application."
  config_space:
    type: str
    required: False
    default: "DEFAULT"
    choices: ["DEFAULT", "SIEM"]
    description: "config space."
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
  description:
    type: str
    required: False
    description: "Description of the application."
  health_check_type:
    type: str
    description: "health check type."
  segment_group_name:
    type: str
    required: False
    description: "segment group name."
  tcp_port_range:
    type: list
    elements: dict
    required: False
    description: "tcp port range"
    suboptions:
      to:
        type: str
        required: False
        description: ""
      from:
        type: str
        required: False
        description: ""
  enabled:
    type: bool
    required: False
    description: "Whether this application is enabled or not."
  domain_names:
    type: list
    elements: str
    required: True
    description: "List of domains and IPs."
  clientless_apps:
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
  state:
    description: "Whether the app should be present or absent."
    type: str
    choices:
        - present
        - absent
    default: present
"""

EXAMPLES = """
- name: Create an app segment
  zscaler.zpacloud.zpa_browser_access:
    name: Example Application
    description: Example Application Test
    enabled: true
    health_reporting: ON_ACCESS
    bypass_type: NEVER
    clientless_apps:
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

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
    deleteNone,
)


def convert_ports_list(obj_list):
    if obj_list is None:
        return []
    r = []
    for o in obj_list:
        if o.get("from", None) is not None and o.get("to", None) is not None:
            r.append("" + o.get("from"))
            r.append("" + o.get("to"))
    return r


def convert_ports(obj_list):
    if obj_list is None:
        return []
    r = []
    for o in obj_list:
        if o.get("from", None) is not None and o.get("to", None) is not None:
            c = (o.get("from"), o.get("to"))
            r.append(c)
    return r


def core(module):
    state = module.params.get("state", None)
    ba_appsegment_id = module.params.get("id", None)
    ba_appsegment_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    app = dict()
    params = [
        "segment_group_id",
        "segment_group_name",
        "bypass_type",
        "clientless_apps",
        "config_space",
        "default_idle_timeout",
        "default_max_age",
        "description",
        "domain_names",
        "double_encrypt",
        "enabled",
        "health_check_type",
        "health_reporting",
        "icmp_access_type",
        "id",
        "ip_anchored",
        "is_cname_enabled",
        "name",
        "passive_health_enabled",
        "tcp_port_range",
        "udp_port_range",
        "server_group_ids",
    ]
    for param_name in params:
        app[param_name] = module.params.get(param_name)
    existing_app = None
    if ba_appsegment_id is not None:
        existing_app = client.app_segments.get_segment(segment_id=ba_appsegment_id)
    elif ba_appsegment_name is not None:
        ba_app_segments = client.app_segments.list_segments().to_list()
        for ba_app_segment in ba_app_segments:
            if ba_app_segment.get("name") == ba_appsegment_name:
                existing_app = ba_app_segment
                break
    if existing_app is not None:
        id = existing_app.get("id")
        existing_app.update(app)
        existing_app["id"] = id
    if state == "present":
        if existing_app is not None:
            """Update"""
            existing_app = deleteNone(
                dict(
                    segment_id=existing_app.get("id"),
                    bypass_type=existing_app.get("bypass_type", None),
                    clientless_app_ids=existing_app.get("clientless_apps", None),
                    config_space=existing_app.get("config_space", None),
                    default_idle_timeout=existing_app.get("default_idle_timeout", None),
                    default_max_age=existing_app.get("default_max_age", None),
                    description=existing_app.get("description", None),
                    domain_names=existing_app.get("domain_names", None),
                    double_encrypt=existing_app.get("double_encrypt", None),
                    enabled=existing_app.get("enabled", None),
                    health_check_type=existing_app.get("health_check_type", None),
                    health_reporting=existing_app.get("health_reporting", None),
                    ip_anchored=existing_app.get("ip_anchored", None),
                    is_cname_enabled=existing_app.get("is_cname_enabled", None),
                    name=existing_app.get("name", None),
                    passive_health_enabled=existing_app.get(
                        "passive_health_enabled", None
                    ),
                    segment_group_id=existing_app.get("segment_group_id", None),
                    server_group_ids=existing_app.get("server_group_ids", None),
                    tcp_ports=convert_ports(existing_app.get("tcp_port_range", None)),
                    udp_ports=convert_ports(existing_app.get("udp_port_range", None)),
                )
            )
            existing_app = client.app_segments.update_segment(**existing_app)
            module.exit_json(changed=True, data=existing_app)
        else:
            """Create"""
            app = deleteNone(
                dict(
                    bypass_type=app.get("bypass_type", None),
                    clientless_app_ids=app.get("clientless_apps", None),
                    config_space=app.get("config_space", None),
                    default_idle_timeout=app.get("default_idle_timeout", None),
                    default_max_age=app.get("default_max_age", None),
                    description=app.get("description", None),
                    domain_names=app.get("domain_names", None),
                    double_encrypt=app.get("double_encrypt", None),
                    enabled=app.get("enabled", None),
                    health_check_type=app.get("health_check_type", None),
                    health_reporting=app.get("health_reporting", None),
                    ip_anchored=app.get("ip_anchored", None),
                    is_cname_enabled=app.get("is_cname_enabled", None),
                    name=app.get("name", None),
                    passive_health_enabled=app.get("passive_health_enabled", None),
                    segment_group_id=app.get("segment_group_id", None),
                    server_group_ids=app.get("server_group_ids", None),
                    tcp_ports=convert_ports_list(app.get("tcp_port_range", None)),
                    udp_ports=convert_ports_list(app.get("udp_port_range", None)),
                )
            )
            app = client.app_segments.add_segment(**app)
            module.exit_json(changed=False, data=app)
    elif state == "absent" and existing_app is not None:
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
    argument_spec.update(
        tcp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        enabled=dict(type="bool", required=False),
        default_idle_timeout=dict(type="str", required=False, default=""),
        bypass_type=dict(
            type="str", required=False, choices=["ALWAYS", "NEVER", "ON_NET"]
        ),
        udp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        config_space=dict(
            type="str", required=False, default="DEFAULT", choices=["DEFAULT", "SIEM"]
        ),
        health_reporting=dict(
            type="str",
            required=False,
            default="NONE",
            choices=["NONE", "ON_ACCESS", "CONTINUOUS"],
        ),
        segment_group_id=dict(type="str", required=True),
        double_encrypt=dict(type="bool", required=False),
        health_check_type=dict(type="str"),
        default_max_age=dict(type="str", required=False, default=""),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", required=False),
        ip_anchored=dict(type="bool", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        icmp_access_type=dict(
            type="str",
            required=False,
            default="NONE",
            choices=["PING_TRACEROUTING", "PING", "NONE"],
        ),
        id=dict(type="str"),
        server_group_ids=dict(type="list", elements="str", required=True),
        segment_group_name=dict(type="str", required=False),
        domain_names=dict(type="list", elements="str", required=True),
        clientless_apps=dict(
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
