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
module: zpa_app_protection_security_profile
short_description: Create, update, or delete Zscaler Private Access (ZPA) app protection security profiles.
description:
    - This Ansible module enables you to manage Zscaler Private Access (ZPA) app protection security profiles in the ZPA Cloud.
    - You can use this module to create new profiles, update existing ones, or delete profiles as needed.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - The Zscaler SDK Python package must be installed. You can install it using pip:
      $ pip install zscaler-sdk-python
options:
    name:
        description: The name of the app protection security profile.
        required: true
        type: str
    description:
        description: A description of the app protection security profile.
        required: false
        type: str
    global_control_actions:
        description: A list of global control actions.
        required: false
        type: list
        elements: str
    incarnation_number:
        description: The incarnation number of the profile.
        required: false
        type: str
    paranoia_level:
        description: The paranoia level of the profile.
        required: false
        type: str
    check_control_deployment_status:
        description: Check control deployment status.
        required: false
        type: bool
    controls_info:
        description: Information about controls.
        required: false
        type: list
        elements: dict
        options:
            control_type:
                description: The control type.
                required: false
                type: str
                choices:
                    - WEBSOCKET_PREDEFINED
                    - WEBSOCKET_CUSTOM
                    - THREATLABZ
                    - CUSTOM
                    - PREDEFINED
            count:
                description: The control count.
                required: false
                type: str
    custom_controls:
        description: Custom controls.
        required: false
        type: list
        elements: dict
        options:
            id:
                description: The control ID.
                required: false
                type: str
            action:
                description: The control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            action_value:
                description: The control action value.
                required: false
                type: str
            associated_inspection_profile_names:
                description: Names of associated inspection profiles.
                required: false
                type: list
                elements: dict
                options:
                    id:
                        description: The inspection profile ID.
                        required: false
                        type: str
                    name:
                        description: The inspection profile name.
                        required: false
                        type: str
            control_number:
                description: The control number.
                required: false
                type: str
            control_rule_json:
                description: The control rule JSON.
                required: false
                type: str
            control_type:
                description: The control type.
                required: false
                type: str
                choices:
                    - WEBSOCKET_PREDEFINED
                    - WEBSOCKET_CUSTOM
                    - THREATLABZ
                    - CUSTOM
                    - PREDEFINED
            default_action:
                description: The default control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            default_action_value:
                description: The default action value.
                required: false
                type: str
            description:
                description: The control description.
                required: false
                type: str
            name:
                description: The control name.
                required: false
                type: str
            paranoia_level:
                description: The paranoia level.
                required: false
                type: str
            protocol_type:
                description: The protocol type.
                required: false
                type: str
                choices:
                    - HTTP
                    - HTTPS
                    - FTP
                    - RDP
                    - SSH
                    - WEBSOCKET
                    - VNC
                    - NONE
            rules:
                description: Control rules.
                required: false
                type: list
                elements: dict
                options:
                    conditions:
                        description: Rule conditions.
                        required: false
                        type: list
                        elements: dict
                        options:
                            lhs:
                                description: The left-hand side of the condition.
                                required: false
                                type: str
                                choices:
                                    - SIZE
                                    - VALUE
                            op:
                                description: The operator for the condition.
                                required: false
                                type: str
                                choices:
                                    - RX
                                    - CONTAINS
                                    - STARTS_WITH
                                    - ENDS_WITH
                                    - EQ
                                    - LE
                                    - GE
                            rhs:
                                description: The right-hand side of the condition.
                                required: false
                                type: str
                    names:
                        description: Control rule names.
                        required: false
                        type: list
                        elements: str
                    type:
                        description: Control rule type.
                        required: false
                        type: str
                        choices:
                            - REQUEST_HEADERS
                            - REQUEST_URI
                            - QUERY_STRING
                            - REQUEST_COOKIES
                            - REQUEST_METHOD
                            - REQUEST_BODY
                            - RESPONSE_HEADERS
                            - RESPONSE_BODY
                            - WS_MAX_PAYLOAD_SIZE
                            - WS_MAX_FRAGMENT_PER_MESSAGE
            severity:
                description: The control severity.
                required: false
                type: str
                choices:
                    - CRITICAL
                    - ERROR
                    - WARNING
                    - INFO
            type:
                description: The control type.
                required: false
                type: str
                choices:
                    - REQUEST
                    - RESPONSE
            version:
                description: The control version.
                required: false
                type: str
    predefined_controls:
        description: Predefined controls.
        required: false
        type: list
        elements: dict
        options:
            action:
                description: The control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            action_value:
                description: The control action value.
                required: false
                type: str
            associated_inspection_profile_names:
                description: Names of associated inspection profiles.
                required: false
                type: list
                elements: dict
                options:
                    id:
                        description: The inspection profile ID.
                        required: false
                        type: str
                    name:
                        description: The inspection profile name.
                        required: false
                        type: str
            attachment:
                description: The control attachment.
                required: false
                type: str
            control_group:
                description: The control group.
                required: false
                type: str
            control_number:
                description: The control number.
                required: false
                type: str
            control_type:
                description: The control type.
                required: false
                type: str
                choices:
                    - WEBSOCKET_PREDEFINED
                    - WEBSOCKET_CUSTOM
                    - THREATLABZ
                    - CUSTOM
                    - PREDEFINED
            default_action:
                description: The default control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            default_action_value:
                description: The default action value.
                required: false
                type: str
            description:
                description: The control description.
                required: false
                type: str
            name:
                description: The control name.
                required: false
                type: str
            paranoia_level:
                description: The paranoia level.
                required: false
                type: str
            protocol_type:
                description: The protocol type.
                required: false
                type: str
                choices:
                    - HTTP
                    - HTTPS
                    - FTP
                    - RDP
                    - SSH
                    - WEBSOCKET
            severity:
                description: The control severity.
                required: false
                type: str
                choices:
                    - CRITICAL
                    - ERROR
                    - WARNING
                    - INFO
            version:
                description: The control version.
                required: false
                type: str
        required: false
    predef_controls_version:
        description: The version of predefined controls.
        required: false
        type: str
    threatlabz_controls:
        description: ThreatLabZ controls.
        required: false
        type: list
        elements: dict
        options:
            action:
                description: The control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            action_value:
                description: The control action value.
                required: false
                type: str
            associated_customers:
                description: Associated customers.
                required: false
                type: list
                elements: dict
                options:
                    customer_id:
                        description: The customer ID.
                        required: false
                        type: str
                    exclude_constellation:
                        description: Exclude constellation.
                        required: false
                        type: bool
                    is_partner:
                        description: Is partner.
                        required: false
                        type: bool
                    name:
                        description: The customer name.
                        required: false
                        type: str
            associated_inspection_profile_names:
                description: Names of associated inspection profiles.
                required: false
                type: list
                elements: dict
                options:
                    id:
                        description: The inspection profile ID.
                        required: false
                        type: str
                    name:
                        description: The inspection profile name.
                        required: false
                        type: str
            attachment:
                description: The control attachment.
                required: false
                type: str
            control_group:
                description: The control group.
                required: false
                type: str
            control_number:
                description: The control number.
                required: false
                type: str
            control_type:
                description: The control type.
                required: false
                type: str
                choices:
                    - WEBSOCKET_PREDEFINED
                    - WEBSOCKET_CUSTOM
                    - THREATLABZ
                    - CUSTOM
                    - PREDEFINED
            default_action:
                description: The default control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            default_action_value:
                description: The default action value.
                required: false
                type: str
            description:
                description: The control description.
                required: false
                type: str
            enabled:
                description: Is the control enabled.
                required: false
                type: bool
            engine_version:
                description: The engine version.
                required: false
                type: str
            id:
                description: The control ID.
                required: false
                type: str
            last_deployment_time:
                description: The last deployment time.
                required: false
                type: str
            name:
                description: The control name.
                required: false
                type: str
            paranoia_level:
                description: The paranoia level.
                required: false
                type: str
            rule_deployment_state:
                description: The rule deployment state.
                required: false
                type: str
                choices:
                    - NEW
                    - IN_PROGRESS
                    - COMPLETED
            rule_metadata:
                description: The rule metadata.
                required: false
                type: str
            rule_processor:
                description: The rule processor.
                required: false
                type: str
            ruleset_name:
                description: The ruleset name.
                required: false
                type: str
            ruleset_version:
                description: The ruleset version.
                required: false
                type: str
            severity:
                description: The control severity.
                required: false
                type: str
                choices:
                    - CRITICAL
                    - ERROR
                    - WARNING
                    - INFO
            version:
                description: The control version.
                required: false
                type: str
            zscaler_info_url:
                description: The Zscaler info URL.
                required: false
                type: str
    websocket_controls:
        description: WebSocket controls.
        required: false
        type: list
        elements: dict
        options:
            action:
                description: The control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            action_value:
                description: The control action value.
                required: false
                type: str
            associated_inspection_profile_names:
                description: Names of associated inspection profiles.
                required: false
                type: list
                elements: dict
                options:
                    id:
                        description: The inspection profile ID.
                        required: false
                        type: str
                    name:
                        description: The inspection profile name.
                        required: false
                        type: str
            control_number:
                description: The control number.
                required: false
                type: str
            control_type:
                description: The control type.
                required: false
                type: str
                choices:
                    - WEBSOCKET_PREDEFINED
                    - WEBSOCKET_CUSTOM
                    - THREATLABZ
                    - CUSTOM
                    - PREDEFINED
            default_action:
                description: The default control action.
                required: false
                type: str
                choices:
                    - PASS
                    - BLOCK
                    - REDIRECT
            default_action_value:
                description: The default action value.
                required: false
                type: str
            description:
                description: The control description.
                required: false
                type: str
            id:
                description: The control ID.
                required: false
                type: str
            name:
                description: The control name.
                required: false
                type: str
            paranoia_level:
                description: The paranoia level.
                required: false
                type: str
            severity:
                description: The control severity.
                required: false
                type: str
                choices:
                    - CRITICAL
                    - ERROR
                    - WARNING
                    - INFO
            version:
                description: The control version.
                required: false
                type: str
    zs_defined_control_choice:
        description: ZS defined control choice.
        required: false
        type: str
        choices:
            - ALL
            - SPECIFIC
  state:
    description: "Whether the app should be present or absent."
    type: str
    choices:
        - present
        - absent
    default: present
"""

EXAMPLES = """
- name: Create Second Application Server
  zscaler.zpacloud.zpa_application_server:
    provider: "{{ zpa_cloud }}"
    name: Example1
    description: Example1
    address: example.acme.com
    enabled: true
    app_server_group_ids: []
"""

RETURN = """
# The newly created application server resource record.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone, normalize_app
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    profile = dict()
    params = [
        "id",
        "name",
        "description",
        "check_control_deployment_status",
        "controls_info",
        "custom_controls",
        "global_control_actions",
        "incarnation_number",
        "paranoia_level",
        "predefined_controls",
        "predef_controls_version",
        "threatlabz_controls",
        "web_socket_controls",
        "zs_defined_control_choice",
    ]
    for param_name in params:
        profile[param_name] = module.params.get(param_name, None)
    profile_id = profile.get("id", None)
    profile_name = profile.get("name", None)

    existing_profile = None
    if profile_id is not None:
        profile_box = client.inspection.get_profile(profile_id=profile_id)
        if profile_box is not None:
            existing_profile = profile_box.to_dict()
    elif profile_name is not None:
        profiles = client.inspection.list_profiles().to_list()
        for profile_ in profiles:
            if profile_.get("name") == profile_name:
                existing_profile = profile_
                break

    # Normalize and compare existing and desired application data
    desired_app = normalize_app(profile)
    current_app = normalize_app(existing_profile) if existing_profile else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_app.items():
        if key not in fields_to_exclude and current_app.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {value}"
            )
    if existing_profile is not None:
        id = existing_profile.get("id")
        existing_profile.update(profile)
        existing_profile["id"] = id

    if state == "present":
        if existing_profile is not None:
            if differences_detected:
                """Update"""
                existing_profile = deleteNone(
                    dict(
                        profile_id=existing_profile.get("id"),
                        name=existing_profile.get("name"),
                        description=existing_profile.get("description"),
                        check_control_deployment_status=existing_profile.get("check_control_deployment_status"),
                        controls_info=existing_profile.get("controls_info"),
                        custom_controls=existing_profile.get("custom_controls"),
                        global_control_actions=existing_profile.get("global_control_actions"),
                        incarnation_number=existing_profile.get("incarnation_number"),
                        paranoia_level=existing_profile.get("paranoia_level"),
                        predefined_controls=existing_profile.get("predefined_controls"),
                        predef_controls_version=existing_profile.get("predef_controls_version"),
                        threatlabz_controls=existing_profile.get("threatlabz_controls"),
                        web_socket_controls=existing_profile.get("web_socket_controls"),
                        zs_defined_control_choice=existing_profile.get("zs_defined_control_choice"),
                    )
                )
                existing_profile = client.inspection.update_profile(**existing_profile).to_dict()
                module.exit_json(changed=True, data=existing_profile)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_profile)
        else:
            """Create"""
            profile = deleteNone(
                dict(
                        name=profile.get("name"),
                        description=profile.get("description"),
                        check_control_deployment_status=profile.get("check_control_deployment_status"),
                        controls_info=profile.get("controls_info"),
                        custom_controls=profile.get("custom_controls"),
                        global_control_actions=profile.get("global_control_actions"),
                        incarnation_number=profile.get("incarnation_number"),
                        paranoia_level=profile.get("paranoia_level"),
                        predefined_controls=profile.get("predefined_controls"),
                        predef_controls_version=profile.get("predef_controls_version"),
                        threatlabz_controls=profile.get("threatlabz_controls"),
                        web_socket_controls=profile.get("web_socket_controls"),
                        zs_defined_control_choice=profile.get("zs_defined_control_choice"),
                )
            )
            profile = client.inspection.add_profile(**profile).to_dict()
            module.exit_json(changed=True, data=profile)
    elif (
        state == "absent"
        and existing_profile is not None
        and existing_profile.get("id") is not None
    ):
        code = client.inspection.delete_profile(profile_id=existing_profile.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_profile)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        global_control_actions=dict(type="list", elements="str", required=False),
        incarnation_number=dict(type="str", required=False),
        paranoia_level=dict(type="str", required=False),
        check_control_deployment_status=dict(type="bool", required=False),

        controls_info=dict(
            type="list",
            elements="dict",
            options=dict(
                control_type=dict(type="str", required=False, choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
                count=dict(type="str", required=False),
            ),
            required=False,
        ),

        custom_controls=dict(
            type="list",
            elements="dict",
            options=dict(
                id=dict(type="str", required=False),
                action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                action_value=dict(type="str", required=False),
                associated_inspection_profile_names=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                    ),
                ),
                control_number=dict(type="str", required=False),
                control_rule_json=dict(type="str", required=False),
                control_type=dict(type="str", required=False, choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
                default_action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                default_action_value=dict(type="str", required=False),
                description=dict(type="str", required=False),
                name=dict(type="str", required=False),
                paranoia_level=dict(type="str", required=False),
                protocol_type=dict(type="str", required=False, choices=["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET", "VNC", "NONE"]),
                rules=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        conditions=dict(
                            type="list",
                            elements="dict",
                            options=dict(
                                lhs=dict(type="str", required=False, choices=["SIZE", "VALUE"]),
                                op=dict(type="str", required=False, choices=["RX", "CONTAINS", "STARTS_WITH", "ENDS_WITH", "EQ", "LE", "GE"]),
                                rhs=dict(type="str", required=False),
                            ),
                        ),
                        names=dict(
                            type="list",
                            elements="str",
                        ),
                        type=dict(type="str", required=False, choices=["REQUEST_HEADERS", "REQUEST_URI", "QUERY_STRING", "REQUEST_COOKIES", "REQUEST_METHOD", "REQUEST_BODY", "RESPONSE_HEADERS", "RESPONSE_BODY", "WS_MAX_PAYLOAD_SIZE", "WS_MAX_FRAGMENT_PER_MESSAGE"]),
                    ),
                ),
                severity=dict(type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]),
                type=dict(type="str", required=False, choices=["REQUEST", "RESPONSE"]),
                version=dict(type="str", required=False),
            ),
            required=False,
        ),

        predefined_controls=dict(
            type="list",
            elements="dict",
            options=dict(
                action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                action_value=dict(type="str", required=False),
                associated_inspection_profile_names=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                    ),
                ),
                attachment=dict(type="str", required=False),
                control_group=dict(type="str", required=False),
                control_number=dict(type="str", required=False),
                control_type=dict(type="str", required=False, choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
                default_action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                default_action_value=dict(type="str", required=False),
                description=dict(type="str", required=False),
                name=dict(type="str", required=False),
                paranoia_level=dict(type="str", required=False),
                protocol_type=dict(type="str", required=False, choices=["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET"]),
                severity=dict(type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]),
                version=dict(type="str", required=False),
            ),
            required=False,
        ),
        predef_controls_version=dict(type="str", required=False),
        threatlabz_controls=dict(
            type="list",
            elements="dict",
            options=dict(
                action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                action_value=dict(type="str", required=False),
                associated_customers=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        customer_id=dict(type="str", required=False),
                        exclude_constellation=dict(type="bool", required=False),
                        is_partner=dict(type="bool", required=False),
                        name=dict(type="str", required=False),
                    ),
                ),
                associated_inspection_profile_names=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                    ),
                ),
                attachment=dict(type="str", required=False),
                control_group=dict(type="str", required=False),
                control_number=dict(type="str", required=False),
                control_type=dict(type="str", required=False, choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
                default_action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                default_action_value=dict(type="str", required=False),
                description=dict(type="str", required=False),
                enabled=dict(type="bool", required=False),
                engine_version=dict(type="str", required=False),
                id=dict(type="str", required=False),
                last_deployment_time=dict(type="str", required=False),
                name=dict(type="str", required=False),
                paranoia_level=dict(type="str", required=False),
                rule_deployment_state=dict(type="str", required=False, choices=["NEW", "IN_PROGRESS", "COMPLETED"]),
                rule_metadata=dict(type="str", required=False),
                rule_processor=dict(type="str", required=False),
                ruleset_name=dict(type="str", required=False),
                ruleset_version=dict(type="str", required=False),
                severity=dict(type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]),
                version=dict(type="str", required=False),
                zscaler_info_url=dict(type="str", required=False),
            ),
            required=False,
        ),
        websocket_controls=dict(
            type="list",
            elements="dict",
            options=dict(
                action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                action_value=dict(type="str", required=False),
                associated_inspection_profile_names=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                    ),
                ),
                control_number=dict(type="str", required=False),
                control_type=dict(type="str", required=False, choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
                default_action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
                default_action_value=dict(type="str", required=False),
                description=dict(type="str", required=False),
                id=dict(type="str", required=False),
                name=dict(type="str", required=False),
                paranoia_level=dict(type="str", required=False),
                severity=dict(type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]),
                version=dict(type="str", required=False),
            ),
            required=False,
        ),
        zs_defined_control_choice=dict(type="str", required=False, choices=["ALL", "SPECIFIC"]),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())

if __name__ == "__main__":
    main()