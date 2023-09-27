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
      - Name of the application.
    required: true
    type: str
  id:
    description:
      - ID of the application.
    required: false
    type: str
  description:
    description:
      - Description of the application.
    required: false
    type: str
  default_max_age:
    description:
      - default_max_age
    required: false
    type: str
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
  double_encrypt:
    description:
      - Whether Double Encryption is enabled or disabled for the app.
    type: bool
    required: false
  icmp_access_type:
    description:
      - icmp access type.
    type: str
    required: false
    choices:
      - PING_TRACEROUTING
      - PING
      - NONE
    default: NONE
  default_idle_timeout:
    description:
      - default idle timeout.
    type: str
    required: false
  passive_health_enabled:
    description:
      - passive health enabled.
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
  config_space:
    description:
      - config space.
    type: str
    required: false
    choices:
      - DEFAULT
      - SIEM
    default: DEFAULT
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
  segment_group_name:
    description:
      - segment group name.
    type: str
    required: false
  health_check_type:
    description:
      - health check type.
    type: str
    required: false
  enabled:
    description:
      - Whether this application is enabled or not.
    type: bool
    required: false
  domain_names:
    description:
      - List of domains and IPs.
    type: list
    elements: str
    required: true
  state:
    description: "Whether the app should be present or absent."
    type: str
    choices:
        - present
        - absent
    default: present
"""

EXAMPLES = """
- name: Create/Update/Delete an application segment.
  zscaler.zpacloud.zpa_application_segment:
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
    client = ZPAClientHelper(module)
    app = dict()
    params = [
        "tcp_port_range",
        "udp_port_range",
        "enabled",
        "default_idle_timeout",
        "bypass_type",
        "config_space",
        "health_reporting",
        "segment_group_id",
        "double_encrypt",
        "health_check_type",
        "default_max_age",
        "is_cname_enabled",
        "passive_health_enabled",
        "ip_anchored",
        "name",
        "description",
        "icmp_access_type",
        "id",
        "server_group_ids",
        "segment_group_name",
        "domain_names",
    ]
    for param_name in params:
        app[param_name] = module.params.get(param_name)
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
            app = client.app_segments.update_segment(**existing_app)
            module.exit_json(changed=True, data=app)
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
        client.app_segments.delete_segment(existing_app.get("id"), force_delete=True)
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
    argument_spec.update(
        tcp_port_range=dict(
            type="list", elements="dict", options=port_spec, required=False
        ),
        enabled=dict(type="bool", required=False),
        default_idle_timeout=dict(type="str", required=False, default=""),
        bypass_type=dict(
            type="str",
            required=False,
            default="NEVER",
            choices=["ALWAYS", "NEVER", "ON_NET"],
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
        id=dict(type="str", required=False),
        server_group_ids=id_name_spec,
        segment_group_name=dict(type="str", required=False),
        domain_names=dict(type="list", elements="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
