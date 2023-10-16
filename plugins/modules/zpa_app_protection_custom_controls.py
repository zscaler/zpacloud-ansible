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
module: zpa_app_protection_custom_controls
short_description: Create, update, or delete Zscaler Private Access (ZPA) app protection custom controls.
description:
    - This Ansible module enables you to manage Zscaler Private Access (ZPA) app protection custom controls in the ZPA Cloud.
    - You can use this module to create new custom controls, update existing ones, or delete custom controls as needed.
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

"""
EXAMPLES = """
- name: Create Second Application Server
  zscaler.zpacloud.zpa_app_protection_custom_controls:
    provider: "{{ zpa_cloud }}"
    name: Example1
    description: Example1
    address: example.acme.com
    enabled: true
    app_server_group_ids: []
"""

RETURN = """
# The newly created app protection custom control resource record.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone, normalize_app, validate_rules
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    control = dict()
    params = [
        "id",
        "name",
        "description",
        "action",
        "action_value",
        "associated_inspection_profile_names",
        "control_number",
        "control_rule_json",
        "control_type",
        "default_action",
        "default_action_value",
        "paranoia_level",
        "protocol_type",
        "rules",
        "severity",
        "type",
        "version",
    ]
    for param_name in params:
        control[param_name] = module.params.get(param_name, None)
    control_id = control.get("id", None)
    control_name = control.get("name", None)

    existing_control = None
    if control_id is not None:
        control_box = client.inspection.get_custom_control(control_id=control_id)
        if control_box is not None:
            existing_control = control_box.to_dict()
    elif control_name is not None:
        controls = client.inspection.list_custom_controls().to_list()
        for control_ in controls:
            if control_.get("name") == control_name:
                existing_control = control_
                break

    # Normalize and compare existing and desired application data
    desired_control = normalize_app(control)
    current_control = normalize_app(existing_control) if existing_control else {}

    # Validate the desired control values
    try:
        validate_rules(desired_control)
    except ValueError as ve:
        module.fail_json(msg=str(ve))

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_control.items():
        if key not in fields_to_exclude and current_control.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_control.get(key)}, Desired: {value}"
            )
    if existing_control is not None:
        id = existing_control.get("id")
        existing_control.update(control)
        existing_control["id"] = id

    if state == "present":
        if existing_control is not None:
            if differences_detected:
                """Update"""
                existing_control.update(control)
                existing_control = deleteNone(
                    dict(
                        control_id=existing_control.get("id"),
                        name=existing_control.get("name"),
                        description=existing_control.get("description"),
                        action_value=existing_control.get("action_value"),
                        associated_inspection_profile_names=existing_control.get("associated_inspection_profile_names"),
                        control_number=existing_control.get("control_number"),
                        control_rule_json=existing_control.get("control_rule_json"),
                        control_type=existing_control.get("control_type"),
                        default_action=existing_control.get("default_action"),
                        default_action_value=existing_control.get("default_action_value"),
                        paranoia_level=existing_control.get("paranoia_level"),
                        protocol_type=existing_control.get("protocol_type"),
                        rules=existing_control.get("rules"),
                        severity=existing_control.get("severity"),
                        type=existing_control.get("type"),
                        version=existing_control.get("version"),
                    )
                )
                # Validate the updated control values before updating
                try:
                    validate_rules(existing_control)
                except ValueError as ve:
                    module.fail_json(msg=str(ve))

                existing_control = client.inspection.update_custom_control(**existing_control).to_dict()
                module.exit_json(changed=True, data=existing_control)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_control)
        else:
            """Create"""
            # Validate desired_control before making API call
            try:
                validate_rules(desired_control)
            except ValueError as ve:
                module.fail_json(msg=str(ve))
            control = deleteNone(
                dict(
                        name=control.get("name"),
                        description=control.get("description"),
                        action_value=control.get("action_value"),
                        associated_inspection_profile_names=control.get("associated_inspection_profile_names"),
                        control_number=control.get("control_number"),
                        control_rule_json=control.get("control_rule_json"),
                        control_type=control.get("control_type"),
                        default_action=control.get("default_action"),
                        default_action_value=control.get("default_action_value"),
                        paranoia_level=control.get("paranoia_level"),
                        protocol_type=control.get("protocol_type"),
                        rules=control.get("rules"),
                        severity=control.get("severity"),
                        type=control.get("type"),
                        version=control.get("version"),
                )
            )
            control = client.inspection.add_custom_control(**control).to_dict()
            module.exit_json(changed=True, data=control)
    elif (
        state == "absent"
        and existing_control is not None
        and existing_control.get("id") is not None
    ):
        code = client.inspection.delete_custom_control(control_id=existing_control.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_control)
    module.exit_json(changed=False, data={})

def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        action=dict(type="str", required=False),
        action_value=dict(type="str", required=False),
        control_number=dict(type="str", required=False),
        control_rule_json=dict(type="str", required=False),
        control_type=dict(type="str", required=False,  choices=["WEBSOCKET_PREDEFINED", "WEBSOCKET_CUSTOM", "THREATLABZ", "CUSTOM", "PREDEFINED"]),
        default_action=dict(type="str", required=False),
        default_action_value=dict(type="str", required=False),
        paranoia_level=dict(type="str", required=False),
        protocol_type=dict(type="str", required=False, choices=["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET", "VNC", "NONE"]),
        type=dict(type="str", required=False, choices=["REQUEST", "RESPONSE"]),
        severity=dict(type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]),
        version=dict(type="str", required=False),

        associated_inspection_profile_names=dict(
            type="list",
            elements="dict",
            options=dict(
                id=dict(type="str", required=False),
                name=dict(type="str", required=False),
            ),
            required=False,
        ),

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
                names=dict(type="list", elements="str", required=False),
                type=dict(type="str", required=False, choices=["REQUEST_HEADERS", "REQUEST_URI", "QUERY_STRING", "REQUEST_COOKIES", "REQUEST_METHOD", "REQUEST_BODY", "RESPONSE_HEADERS", "RESPONSE_BODY", "WS_MAX_PAYLOAD_SIZE", "WS_MAX_FRAGMENT_PER_MESSAGE"]),
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
