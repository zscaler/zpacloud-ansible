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
module: zpa_application_segment
short_description: Create an application segment in the ZPA Cloud.
description:
    - This module will create/update/delete an application segment
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
      - The unique identifier of the application resource.
    required: false
    type: str
  name:
    description:
      - The name of the application resource.
    required: true
    type: str
  description:
    description:
      - The description of the application resource.
    required: false
    type: str
  enabled:
    description:
      - Whether this application resource is enabled or not.
    type: bool
    required: false
  ip_anchored:
    description:
      - Whether Source IP Anchoring for use with ZIA is enabled or disabled for the application.
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
  double_encrypt:
    description:
      - Whether Double Encryption is enabled or disabled for the application..
    type: bool
    required: false
    default: false
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
      - Indicates if passive health checks are enabled on the application..
    type: bool
    required: false
    default: true
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
  bypass_on_reauth:
    description:
      - Indicates whether application access during reauthentication bypasses ZPA (Enabled) or not (Disabled).
      - This feature is only applicable for Zscaler Client Connector-specific applications.
    type: bool
    required: false
    default: false
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
    required: false
  segment_group_id:
    description:
      - ID of the segment group.
    type: str
    required: false
  health_check_type:
    description:
      - health check type.
    type: str
    required: false
    default: DEFAULT
  domain_names:
    description:
      - The list of domains and IPs. The maximum limit for domains or IPs is 2,000 applications per application segment
      - The maximum limit for domains or IPs for the whole customer is 6,000 applications.
    type: list
    elements: str
    required: false
  match_style:
    description:
      - Indicates if Multimatch is enabled for the application segment.
      - If enabled (INCLUSIVE), the request allows traffic to match multiple applications.
      - If disabled (EXCLUSIVE), the request allows traffic to match a single application.
      - A domain can only be INCLUSIVE or EXCLUSIVE, and any application segment can only contain inclusive or exclusive domains.
      - A domain can only be INCLUSIVE or EXCLUSIVE, and any application segment can only contain inclusive or exclusive domains
    type: str
    required: false
    choices:
      - EXCLUSIVE
      - INCLUSIVE
    default: EXCLUSIVE
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
    convert_bool_to_str,
    convert_ports,
    convert_ports_list,
    collect_all_items,
    normalize_app,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def warn_drift(module, desired, actual):
    """
    Compare desired vs. actual, warn about any differences.
    This helps track down which attributes are the culprit for drift.
    """
    for key, desired_val in desired.items():
        actual_val = actual.get(key)
        # If both are lists, compare sorted versions to ignore order
        if isinstance(desired_val, list) or isinstance(actual_val, list):
            if sorted(desired_val or []) != sorted(actual_val or []):
                module.warn(
                    f"[POST-UPDATE DRIFT] Key='{key}' => Desired={desired_val}, Actual={actual_val}"
                )
        else:
            if desired_val != actual_val:
                module.warn(
                    f"[POST-UPDATE DRIFT] Key='{key}' => Desired={desired_val}, Actual={actual_val}"
                )


def normalize_app(app):
    """Normalize application segment data, handling port ranges specially"""
    if not app:
        return {}

    normalized = {k: v for k, v in app.items() if v is not None}

    # Ensure both port range formats are present and consistent
    for proto in ["tcp", "udp"]:
        range_key = f"{proto}_port_range"
        ranges_key = f"{proto}_port_ranges"

        # If we have one format but not the other, create the missing one
        if range_key in normalized and ranges_key not in normalized:
            if normalized[range_key]:
                normalized[ranges_key] = []
                for r in normalized[range_key]:
                    if "from" in r and "to" in r:
                        normalized[ranges_key].extend([r["from"], r["to"]])

        elif ranges_key in normalized and range_key not in normalized:
            if normalized[ranges_key]:
                normalized[range_key] = [
                    {"from": p[0], "to": p[1]}
                    for p in convert_ports(normalized[ranges_key])
                ]

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    app = dict()

    params = [
        "id",
        "microtenant_id",
        "name",
        "description",
        "tcp_port_range",
        "tcp_port_ranges",
        "udp_port_range",
        "udp_port_ranges",
        "tcp_protocols",
        "udp_protocols",
        "adp_enabled",
        "enabled",
        "bypass_type",
        "fqdn_dns_check",
        "weighted_load_balancing",
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
        "segment_group_id",
        "server_group_ids",
        "domain_names",
        "match_style",
        "bypass_on_reauth",
    ]

    for param_name in params:
        app[param_name] = module.params.get(param_name)

    # Convert tcp_keep_alive from bool → "0"/"1"
    tcp_keep_alive = module.params.get("tcp_keep_alive")
    converted_tcp_keep_alive = convert_bool_to_str(
        tcp_keep_alive, true_value="1", false_value="0"
    )
    app["tcp_keep_alive"] = converted_tcp_keep_alive

    # Convert icmp_access_type from bool → "PING"/"NONE"
    icmp_access_type = module.params.get("icmp_access_type")
    if isinstance(icmp_access_type, bool):
        app["icmp_access_type"] = "PING" if icmp_access_type else "NONE"
    else:
        module.fail_json(
            msg=f"Invalid value for icmp_access_type: {icmp_access_type}. Only boolean values are allowed."
        )

    # Validate select_connector_close_to_app vs. udp_port_range
    select_connector_close_to_app = module.params.get("select_connector_close_to_app")
    udp_port_range = module.params.get("udp_port_range")
    if select_connector_close_to_app and udp_port_range is not None:
        module.fail_json(
            msg=(
                "Invalid configuration: 'select_connector_close_to_app' cannot be "
                "set to True when 'udp_port_range' is defined."
            )
        )

    segment_id = module.params.get("id")
    segment_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_app = None
    # -- Lookup existing resource
    if segment_id:
        result, _, error = client.application_segment.get_segment(
            segment_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching application segment with id {segment_id}: {to_native(error)}"
            )
        existing_app = result.as_dict()
    else:
        result, error = collect_all_items(
            client.application_segment.list_segments, query_params
        )
        if error:
            module.fail_json(
                msg=f"Error listing application segments: {to_native(error)}"
            )
        if result:
            for segment_ in result:
                if segment_.name == segment_name:
                    existing_app = segment_.as_dict()
                    break

    desired_app = normalize_app(app)
    current_app = normalize_app(existing_app) if existing_app else {}

    # Convert server_groups -> server_group_ids in current_app
    if "server_groups" in current_app:
        current_app["server_group_ids"] = sorted(
            [g.get("id") for g in current_app.get("server_groups", []) if g.get("id")]
        )
        del current_app["server_groups"]

    # Ensure server_group_ids is sorted in desired_app for accurate comparison
    if "server_group_ids" in desired_app and desired_app["server_group_ids"]:
        desired_app["server_group_ids"] = sorted(desired_app["server_group_ids"])

    # Compare for drift
    fields_to_exclude = ["id"]
    differences_detected = False
    for key, desired_val in desired_app.items():
        if key in fields_to_exclude:
            continue
        current_val = current_app.get(key)

        if key == "domain_names":
            # Compare sorted lists
            if sorted(current_val or []) != sorted(desired_val or []):
                differences_detected = True
                module.warn(
                    f"Difference detected in domain_names. "
                    f"Current={sorted(current_val or [])}, Desired={sorted(desired_val or [])}"
                )
        else:
            if current_val != desired_val:
                differences_detected = True
                module.warn(
                    f"Difference detected in {key}. Current={current_val}, Desired={desired_val}"
                )

    # Check Mode
    if module.check_mode:
        if state == "present" and (existing_app is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_app is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    # If resource exists, unify the IDs
    if existing_app:
        id_ = existing_app.get("id")
        existing_app.update(app)
        existing_app["id"] = id_

    module.warn(f"Final payload being sent to SDK: {app}")

    # ----------------- STATE: PRESENT -----------------
    if state == "present":
        if existing_app:
            if differences_detected:
                # Build update payload
                update_segment = deleteNone(
                    {
                        "segment_id": existing_app.get("id"),
                        "microtenant_id": desired_app.get("microtenant_id"),
                        "name": desired_app.get("name"),
                        "description": desired_app.get("description"),
                        "enabled": desired_app.get("enabled"),
                        "adp_enabled": desired_app.get("adp_enabled"),
                        "bypass_type": desired_app.get("bypass_type"),
                        "bypass_on_reauth": desired_app.get("bypass_on_reauth"),
                        "domain_names": desired_app.get("domain_names"),
                        "double_encrypt": desired_app.get("double_encrypt"),
                        "health_check_type": desired_app.get("health_check_type"),
                        "health_reporting": desired_app.get("health_reporting"),
                        "ip_anchored": desired_app.get("ip_anchored"),
                        "is_cname_enabled": desired_app.get("is_cname_enabled"),
                        "fqdn_dns_check": desired_app.get("fqdn_dns_check"),
                        "weighted_load_balancing": desired_app.get(
                            "weighted_load_balancing"
                        ),
                        "tcp_keep_alive": desired_app.get("tcp_keep_alive"),
                        "icmp_access_type": desired_app.get("icmp_access_type"),
                        "select_connector_close_to_app": desired_app.get(
                            "select_connector_close_to_app"
                        ),
                        "use_in_dr_mode": desired_app.get("use_in_dr_mode"),
                        "is_incomplete_dr_config": desired_app.get(
                            "is_incomplete_dr_config"
                        ),
                        "inspect_traffic_with_zia": desired_app.get(
                            "inspect_traffic_with_zia"
                        ),
                        "match_style": desired_app.get("match_style"),
                        "passive_health_enabled": desired_app.get(
                            "passive_health_enabled"
                        ),
                        "segment_group_id": desired_app.get("segment_group_id"),
                        "server_group_ids": desired_app.get("server_group_ids"),
                        "tcp_port_ranges": convert_ports(
                            existing_app.get("tcp_port_range", None)
                        ),
                        "udp_port_ranges": convert_ports(
                            existing_app.get("udp_port_range", None)
                        ),
                        "tcp_protocols": desired_app.get("tcp_protocols"),
                        "udp_protocols": desired_app.get("udp_protocols"),
                    }
                )
                module.warn(f"Payload Update for SDK: {update_segment}")

                # Update
                updated_segment, _, error = client.application_segment.update_segment(
                    segment_id=update_segment.pop("segment_id"), **existing_app
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating application segment: {to_native(error)}"
                    )

                # -- After update, fetch the newly-updated resource and compare
                #    to desired_app for final drift detection.
                refreshed, _, err = client.application_segment.get_segment(
                    updated_segment.id,
                    query_params={"microtenant_id": desired_app.get("microtenant_id")},
                )
                if err:
                    module.warn(
                        f"[POST-UPDATE] Failed to retrieve updated resource by ID. Error: {to_native(err)}"
                    )
                else:
                    final_app = normalize_app(refreshed.as_dict())
                    warn_drift(module, desired_app, final_app)

                module.exit_json(changed=True, data=updated_segment.as_dict())
            else:
                module.exit_json(changed=False, data=existing_app)

        else:
            # Create
            module.warn("Creating app segment as no existing app segment was found")
            create_segment = deleteNone(
                {
                    "microtenant_id": desired_app.get("microtenant_id"),
                    "name": desired_app.get("name"),
                    "description": desired_app.get("description"),
                    "enabled": desired_app.get("enabled"),
                    "adp_enabled": desired_app.get("adp_enabled"),
                    "bypass_type": desired_app.get("bypass_type"),
                    "bypass_on_reauth": desired_app.get("bypass_on_reauth"),
                    "domain_names": desired_app.get("domain_names"),
                    "double_encrypt": desired_app.get("double_encrypt"),
                    "health_check_type": desired_app.get("health_check_type"),
                    "health_reporting": desired_app.get("health_reporting"),
                    "ip_anchored": desired_app.get("ip_anchored"),
                    "fqdn_dns_check": desired_app.get("fqdn_dns_check"),
                    "weighted_load_balancing": desired_app.get(
                        "weighted_load_balancing"
                    ),
                    "is_cname_enabled": desired_app.get("is_cname_enabled"),
                    "tcp_keep_alive": desired_app.get("tcp_keep_alive"),
                    "icmp_access_type": desired_app.get("icmp_access_type"),
                    "match_style": desired_app.get("match_style"),
                    "passive_health_enabled": desired_app.get("passive_health_enabled"),
                    "select_connector_close_to_app": desired_app.get(
                        "select_connector_close_to_app"
                    ),
                    "use_in_dr_mode": desired_app.get("use_in_dr_mode"),
                    "is_incomplete_dr_config": desired_app.get(
                        "is_incomplete_dr_config"
                    ),
                    "inspect_traffic_with_zia": desired_app.get(
                        "inspect_traffic_with_zia"
                    ),
                    "segment_group_id": desired_app.get("segment_group_id"),
                    "server_group_ids": desired_app.get("server_group_ids"),
                    "tcp_port_ranges": convert_ports_list(
                        app.get("tcp_port_range", None)
                    ),
                    "udp_port_ranges": convert_ports_list(
                        app.get("udp_port_range", None)
                    ),
                    "tcp_protocols": desired_app.get("tcp_protocols"),
                    "udp_protocols": desired_app.get("udp_protocols"),
                }
            )
            module.warn(f"Payload for SDK: {create_segment}")
            new_segment, _, error = client.application_segment.add_segment(
                **create_segment
            )
            if error:
                module.fail_json(
                    msg=f"Error creating application segment: {to_native(error)}"
                )

            # -- After creation, fetch the newly-created resource for drift check
            refreshed, _, err = client.application_segment.get_segment(
                new_segment.id,
                query_params={"microtenant_id": desired_app.get("microtenant_id")},
            )
            if err:
                module.warn(
                    f"[POST-CREATE] Failed to retrieve newly created resource. Error: {to_native(err)}"
                )
            else:
                final_app = normalize_app(refreshed.as_dict())
                warn_drift(module, desired_app, final_app)

            module.exit_json(changed=True, data=new_segment.as_dict())

    # ----------------- STATE: ABSENT -----------------
    elif state == "absent":
        if existing_app:
            _, _, error = client.application_segment.delete_segment(
                segment_id=existing_app.get("id"),
                microtenant_id=microtenant_id,
            )
            if error:
                module.fail_json(
                    msg=f"Error deleting application segment: {to_native(error)}"
                )
            module.exit_json(changed=True, data=existing_app)
        module.exit_json(changed=False, data={})

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    port_spec = dict(to=dict(type="str", required=False))
    port_spec["from"] = dict(type="str", required=False)
    id_name_spec = dict(type="list", elements="str", required=False)
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        adp_enabled=dict(type="bool", required=False),
        select_connector_close_to_app=dict(type="bool", default=False, required=False),
        use_in_dr_mode=dict(type="bool", required=False, default=False),
        is_incomplete_dr_config=dict(type="bool", required=False),
        fqdn_dns_check=dict(type="bool", required=False, default=False),
        inspect_traffic_with_zia=dict(type="bool", required=False),
        weighted_load_balancing=dict(type="bool", required=False, default=False),
        bypass_type=dict(
            type="str",
            required=False,
            default="NEVER",
            choices=["ALWAYS", "NEVER", "ON_NET"],
        ),
        bypass_on_reauth=dict(type="bool", required=False, default=False),
        health_reporting=dict(
            type="str",
            required=False,
            default="NONE",
            choices=["NONE", "ON_ACCESS", "CONTINUOUS"],
        ),
        tcp_keep_alive=dict(type="bool", required=False),
        segment_group_id=dict(type="str", required=False),
        double_encrypt=dict(type="bool", default=False, required=False),
        health_check_type=dict(type="str", default="DEFAULT", required=False),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", default=True, required=False),
        ip_anchored=dict(type="bool", required=False),
        match_style=dict(
            type="str",
            required=False,
            default="EXCLUSIVE",
            choices=["EXCLUSIVE", "INCLUSIVE"],
        ),
        icmp_access_type=dict(type="bool", required=False),
        server_group_ids=id_name_spec,
        domain_names=dict(type="list", elements="str", required=False),
        tcp_protocols=dict(type="list", elements="str", required=False),
        udp_protocols=dict(type="list", elements="str", required=False),
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
