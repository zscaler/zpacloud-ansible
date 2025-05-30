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
module: zpa_application_segment_inspection
short_description: Create an AppProtection application segment in the ZPA Cloud.
description:
    - This module will create/update/delete an AppProtection application segment
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
      - Indicates if passive health checks are enabled on the application..
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
  fqdn_dns_check:
    description:
      - If set to true, performs a DNS check to find an A or AAAA record for this application.
    type: bool
    required: false
  adp_enabled:
    description:
      - Indicates if Active Directory Inspection is enabled or not for the application.
      - This allows the application segment's traffic to be inspected by Active Directory (AD) Protection.
      - By default, this field is set to false.
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
      - The list of domains and IPs. The maximum limit for domains or IPs is 2,000 applications per application segment
      - The maximum limit for domains or IPs for the whole customer is 6,000 applications.
    type: list
    elements: str
    required: true
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
  common_apps_dto:
    type: dict
    required: true
    description: "List of applications e.g., inspection or Browser Access"
    suboptions:
      apps_config:
        type: list
        elements: dict
        required: true
        description: "List of applications to be configured"
        suboptions:
          name:
            description: "The name of the application"
            type: str
            required: true
          description:
            description: "The description of the application"
            type: str
            required: false
          enabled:
            description: "Whether the application is enabled"
            type: bool
            required: false
          trust_untrusted_cert:
            description: "Whether the use of untrusted certificates is enabled or disabled for the Browser Access application"
            type: bool
            required: false
          allow_options:
            description: "Whether the options are enabled for the Browser Access application or not"
            type: bool
            required: false
          app_types:
            description: "This denotes the operation type"
            type: list
            elements: str
            required: true
            choices: ["INSPECT"]
          application_port:
            description: "Port for the inspection application"
            type: str
            required: true
          application_protocol:
            description: "Protocol for the inspection application"
            type: str
            required: true
            choices: ["HTTP", "HTTPS"]
          certificate_id:
            description: "The unique identifier of the Browser Access certificate."
            type: str
            required: false
          domain:
            description: "The domain of the application"
            type: str
            required: true
"""

EXAMPLES = """
- name: Create/Update/Delete an application segment.
  zscaler.zpacloud.zpa_application_segment_inspection:
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
    collect_all_items,
    convert_ports_list,
    map_pra_apps_to_common_apps,
    normalize_port_processing,
    normalize_app,
    warn_drift,
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
        "tcp_port_ranges",
        "udp_port_ranges",
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
        "common_apps_dto",
        "segment_group_id",
        "server_group_ids",
        "domain_names",
        "fqdn_dns_check",
    ]
    for param_name in params:
        app[param_name] = module.params.get(param_name)

    common_apps_dto = module.params.get("common_apps_dto")
    if common_apps_dto:
        app["common_apps_dto"] = common_apps_dto

    select_connector_close_to_app = module.params.get(
        "select_connector_close_to_app", None
    )
    udp_port_range = module.params.get("udp_port_range", None)

    if select_connector_close_to_app and udp_port_range is not None:
        module.fail_json(
            msg="Invalid configuration: 'select_connector_close_to_app' cannot be set to True when 'udp_port_range' is defined."
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
        result, _unused, error = client.app_segments_inspection.get_segment_inspection(
            segment_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching application segment with id {segment_id}: {to_native(error)}"
            )
        existing_app = result.as_dict()
    else:
        result, error = collect_all_items(
            client.app_segments_inspection.list_segment_inspection, query_params
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

    desired_app = normalize_app(normalize_port_processing(app))
    current_app = (
        normalize_app(normalize_port_processing(existing_app)) if existing_app else {}
    )

    # Convert server_groups -> server_group_ids in current_app
    if "server_groups" in current_app:
        current_app["server_group_ids"] = sorted(
            [g.get("id") for g in current_app.get("server_groups", []) if g.get("id")]
        )
        del current_app["server_groups"]

    # Ensure server_group_ids is sorted in desired_app for accurate comparison
    if "server_group_ids" in desired_app and desired_app["server_group_ids"]:
        desired_app["server_group_ids"] = sorted(desired_app["server_group_ids"])

    fields_to_exclude = ["id", "common_apps_dto"]
    # Special comparison for common_apps_dto
    if "common_apps_dto" in desired_app:
        current_inspect_apps = current_app.get("inspection_apps", [])
        desired_apps_config = desired_app["common_apps_dto"].get("apps_config", [])

        # Convert current inspectionApps to the same format as desired apps_config
        normalized_current = map_pra_apps_to_common_apps(current_inspect_apps)
        normalized_current_apps = normalized_current.get("apps_config", [])

        # Compare the normalized versions
        if sorted(normalized_current_apps, key=lambda x: x.get("domain", "")) != sorted(
            desired_apps_config, key=lambda x: x.get("domain", "")
        ):
            differences_detected = True
            # module.warn(
            #     f"Difference detected in application configurations. "
            #     f"Current: {normalized_current_apps}, Desired: {desired_apps_config}"
            # )

    differences_detected = False

    for key, desired_value in desired_app.items():
        if key in fields_to_exclude:
            continue

        current_value = current_app.get(key)

        if key == "domain_names":
            # Compare them as sorted lists to ignore order differences
            if sorted(current_value or []) != sorted(desired_value or []):
                differences_detected = True
                # module.warn(
                #     f"Difference detected in domain_names. "
                #     f"Current (sorted): {sorted(current_value or [])}, "
                #     f"Desired (sorted): {sorted(desired_value or [])}"
                # )
        else:
            # Normal comparison for everything else
            if current_value != desired_value:
                differences_detected = True
                # module.warn(
                #     f"Difference detected in {key}. "
                #     f"Current: {current_value}, Desired: {desired_value}"
                # )
                # module.warn(
                #     f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {desired_value}"
                # )

    if module.check_mode:
        if state == "present" and (existing_app is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_app is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if module.check_mode:
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

    # Enrich common_apps_dto with app_id/inspect_app_id and detect deletions
    # ------------------------------------------------------------------
    # Enrich common_apps_dto with app_id / inspect_app_id and detect deletions
    # ------------------------------------------------------------------
    if "common_apps_dto" in desired_app:
        desired_configs = desired_app["common_apps_dto"].get("apps_config", [])

        segments_list, err = collect_all_items(
            lambda qp: client.app_segment_by_type.get_segments_by_type(
                application_type="INSPECT",
                expand_all=False,
                # only filter by appId when we are updating
                query_params={"appId": existing_app["id"]} if existing_app else {},
            ),
            query_params={},
        )
        if err:
            module.fail_json(msg=f"Failed to fetch inspection apps: {to_native(err)}")

        # ------ extra debug so we know what came back ------
        module.warn(f"[DEBUG] fetched {len(segments_list)} inspection segment(s)")

        if existing_app:
            target_app_id = existing_app.get("id")
            module.warn(f"[DEBUG] existing_app.id = {target_app_id}")
            pra_by_domain = {
                getattr(s, "domain"): s
                for s in segments_list
                if getattr(s, "app_id", None) == target_app_id
            }
        else:
            module.warn("[DEBUG] existing_app is None (create flow)")
            pra_by_domain = {getattr(s, "domain"): s for s in segments_list}

        updated_configs = []
        deleted_ids = []
        found_domains = set()

        for config in desired_configs:
            domain = config.get("domain")
            pra_app = pra_by_domain.get(domain)

            # on create we do not have an app_id yet
            config["app_id"] = existing_app["id"] if existing_app else ""
            if pra_app:
                config["inspect_app_id"] = pra_app.id
                found_domains.add(domain)
            else:
                config["inspect_app_id"] = ""

            updated_configs.append(config)

        for domain, pra in pra_by_domain.items():
            if domain not in found_domains:
                deleted_ids.append(pra.id)

        desired_app["common_apps_dto"]["apps_config"] = updated_configs
        if deleted_ids:
            desired_app["common_apps_dto"]["deleted_pra_apps"] = deleted_ids

        desired_app["domain_names"] = [
            a["domain"] for a in updated_configs if a.get("domain")
        ]
        desired_app["tcp_port_range"] = [
            {"from": a["application_port"], "to": a["application_port"]}
            for a in updated_configs
            if a.get("application_port")
        ]

    if state == "present":
        if existing_app:
            if differences_detected:
                update_segment = deleteNone(
                    dict(
                        segment_id=existing_app.get("id"),
                        microtenant_id=desired_app.get("microtenant_id"),
                        name=desired_app.get("name", None),
                        description=desired_app.get("description", None),
                        enabled=desired_app.get("enabled", None),
                        bypass_type=desired_app.get("bypass_type", None),
                        domain_names=desired_app.get("domain_names", None),
                        double_encrypt=desired_app.get("double_encrypt", None),
                        health_check_type=desired_app.get("health_check_type", None),
                        health_reporting=desired_app.get("health_reporting", None),
                        ip_anchored=desired_app.get("ip_anchored", None),
                        is_cname_enabled=desired_app.get("is_cname_enabled", None),
                        tcp_keep_alive=desired_app.get("tcp_keep_alive", None),
                        icmp_access_type=desired_app.get("icmp_access_type", None),
                        fqdn_dns_check=desired_app.get("fqdn_dns_check", None),
                        select_connector_close_to_app=desired_app.get(
                            "select_connector_close_to_app", None
                        ),
                        use_in_dr_mode=desired_app.get("use_in_dr_mode", None),
                        is_incomplete_dr_config=desired_app.get(
                            "is_incomplete_dr_config", None
                        ),
                        inspect_traffic_with_zia=desired_app.get(
                            "inspect_traffic_with_zia", None
                        ),
                        common_apps_dto=desired_app.get("common_apps_dto", None),
                        passive_health_enabled=desired_app.get(
                            "passive_health_enabled", None
                        ),
                        segment_group_id=desired_app.get("segment_group_id", None),
                        server_group_ids=desired_app.get("server_group_ids", None),
                        tcp_port_ranges=convert_ports_list(
                            existing_app.get("tcp_port_range", None)
                        ),
                        udp_port_ranges=convert_ports_list(
                            existing_app.get("udp_port_range", None)
                        ),
                    )
                )

                # module.warn(f"Payload Update for SDK: {update_segment}")
                updated_segment, _unused, error = (
                    client.app_segments_pra.update_segment_pra(
                        segment_id=update_segment.pop("segment_id"), **update_segment
                    )
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating application segment: {to_native(error)}"
                    )

                refreshed, _unused, err = client.app_segments_pra.get_segment_pra(
                    updated_segment.id,
                    query_params={"microtenant_id": desired_app.get("microtenant_id")},
                )
                if err:
                    module.warn(
                        f"[POST-UPDATE] Failed to retrieve updated resource by ID. Error: {to_native(err)}"
                    )
                else:
                    final_app = normalize_port_processing(refreshed.as_dict())
                    warn_drift(module, desired_app, final_app)

                module.exit_json(changed=True, data=updated_segment.as_dict())
            else:
                module.exit_json(changed=False, data=existing_app)

        else:
            """Create"""
            create_inspect_segment = deleteNone(
                dict(
                    microtenant_id=desired_app.get("microtenant_id", None),
                    name=desired_app.get("name", None),
                    description=desired_app.get("description", None),
                    enabled=desired_app.get("enabled", None),
                    bypass_type=desired_app.get("bypass_type", None),
                    domain_names=desired_app.get("domain_names", None),
                    double_encrypt=desired_app.get("double_encrypt", None),
                    health_check_type=desired_app.get("health_check_type", None),
                    health_reporting=desired_app.get("health_reporting", None),
                    ip_anchored=desired_app.get("ip_anchored", None),
                    is_cname_enabled=desired_app.get("is_cname_enabled", None),
                    tcp_keep_alive=desired_app.get("tcp_keep_alive", None),
                    icmp_access_type=desired_app.get("icmp_access_type", None),
                    fqdn_dns_check=desired_app.get("fqdn_dns_check", None),
                    passive_health_enabled=desired_app.get(
                        "passive_health_enabled", None
                    ),
                    select_connector_close_to_app=desired_app.get(
                        "select_connector_close_to_app", None
                    ),
                    use_in_dr_mode=desired_app.get("use_in_dr_mode", None),
                    common_apps_dto=desired_app.get("common_apps_dto", None),
                    is_incomplete_dr_config=desired_app.get(
                        "is_incomplete_dr_config", None
                    ),
                    inspect_traffic_with_zia=desired_app.get(
                        "inspect_traffic_with_zia", None
                    ),
                    segment_group_id=desired_app.get("segment_group_id", None),
                    server_group_ids=desired_app.get("server_group_ids", None),
                    tcp_port_ranges=convert_ports_list(app.get("tcp_port_range", None)),
                    udp_port_ranges=convert_ports_list(app.get("udp_port_range", None)),
                )
            )
            module.warn(f"Payload for SDK: {create_inspect_segment}")
            new_segment, _unused, error = (
                client.app_segments_inspection.add_segment_inspection(
                    **create_inspect_segment
                )
            )
            if error:
                module.fail_json(
                    msg=f"Error creating application segment: {to_native(error)}"
                )

            # -- After creation, fetch the newly-created resource for drift check
            refreshed, _unused, err = (
                client.app_segments_inspection.get_segment_inspection(
                    new_segment.id,
                    query_params={"microtenant_id": desired_app.get("microtenant_id")},
                )
            )
            if err:
                module.warn(
                    f"[POST-CREATE] Failed to retrieve newly created resource. Error: {to_native(err)}"
                )
            else:
                final_app = normalize_port_processing(refreshed.as_dict())
                warn_drift(module, desired_app, final_app)

            module.exit_json(changed=True, data=new_segment.as_dict())

    elif state == "absent":
        if existing_app:
            _unused, _unused, error = (
                client.app_segments_inspection.delete_segment_inspection(
                    segment_id=existing_app.get("id"),
                    microtenant_id=microtenant_id,
                )
            )
            if error:
                module.fail_json(
                    msg=f"Error deleting inspection application segment: {to_native(error)}"
                )
            module.exit_json(changed=True, data=existing_app)
        module.exit_json(changed=False, data={})

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
        app_types=dict(type="list", elements="str", choices=["INSPECT"], required=True),
        application_port=dict(type="str", required=True),
        application_protocol=dict(type="str", choices=["HTTP", "HTTPS"], required=True),
        certificate_id=dict(type="str", required=False),
        trust_untrusted_cert=dict(type="bool", required=False),
        allow_options=dict(type="bool", required=False),
        domain=dict(type="str", required=True),
    )
    argument_spec.update(
        id=dict(type="str", required=False),
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
        tcp_keep_alive=dict(type="bool", required=False),
        segment_group_id=dict(type="str", required=True),
        double_encrypt=dict(type="bool", required=False),
        health_check_type=dict(type="str"),
        is_cname_enabled=dict(type="bool", required=False),
        passive_health_enabled=dict(type="bool", required=False),
        ip_anchored=dict(type="bool", required=False),
        icmp_access_type=dict(type="bool", required=False),
        fqdn_dns_check=dict(type="bool", required=False),
        domain_names=dict(type="list", elements="str", required=True),
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
        server_group_ids=id_name_spec,
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
