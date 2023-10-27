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
module: zpa_app_protection_custom_control
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
        description: The name of the custom control.
        required: true
        type: str
    description:
        description: The description of the custom control.
        required: false
        type: str
    action:
        description: The action of the custom control.
        required: false
        type: str
        choices:
            - PASS
            - BLOCK
            - REDIRECT
    action_value:
        description: Denotes the action. Supports any string.
        required: false
        type: str
    default_action:
        description: The performed action.
        required: false
        type: str
        choices:
            - PASS
            - BLOCK
            - REDIRECT
    default_action_value:
        description: Used to provide the redirect URL if the default action is set to REDIRECT.
        required: false
        type: str
    control_rule_json:
        description: The control rule in JSON format that has the conditions and type of control for the AppProtection control.
        required: false
        type: str
    control_type:
        description: The control type of the custom control.
        required: false
        type: str
        choices:
            - WEBSOCKET_PREDEFINED
            - WEBSOCKET_CUSTOM
            - THREATLABZ
            - CUSTOM
            - PREDEFINED
    paranoia_level:
        description: The OWASP Predefined Paranoia Level.
        required: false
        type: str
        choices:
            - '1'
            - '2'
            - '3'
            - '4'
    protocol_type:
        description: The protocol type of the custom control.
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
    severity:
        description: The severity of the AppProtection control number.
        required: false
        type: str
        choices:
            - CRITICAL
            - ERROR
            - WARNING
            - INFO
    type:
        description: The rules to be applied to the request or response type.
        required: false
        type: str
        choices:
            - CRITICAL
            - ERROR
            - WARNING
            - INFO
  rules:
    type: list
    elements: dict
    required: False
    description: "The rules of the custom controls applied as conditions"
    suboptions:
      conditions:
        required: False
        description: "The conditions of the AppProtection rule"
        type: list
        elements: dict
        suboptions:
          lhs:
            description: "The key for the object type"
            type: str
            required: False
            choices:
                - SIZE
                - VALUE
          op:
            description: "The operation type"
            type: str
            required: False
            choices:
                - RX
                - CONTAINS
                - STARTS_WITH
                - ENDS_WITH
                - EQ
                - LE
                - GE
          rhs:
            description: "The value for the given object type. Its value depends upon the key."
            type: str
            required: False
      names:
        description: "The names of the AppProtection rule"
        type: list
        elements: str
        required: true
    type:
        description: The type of the AppProtection rule.
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
"""
EXAMPLES = """
- name: Create App Protection Custom Control
      zscaler.zpacloud.zpa_app_protection_custom_controls:
        provider: "{{ zpa_cloud }}"
        name: "Example_App_Protection_Custom_Control"
        description: "Example_App_Protection_Custom_Control"
        action: "PASS"
        default_action: PASS
        paranoia_level: "2"
        severity: "CRITICAL"
        type: "REQUEST"
        protocol_type: "HTTP"
        rules:
          - conditions:
              - lhs: VALUE
                op: RX
                rhs: "test"
              - lhs: SIZE
                op: EQ
                rhs: "1000"
            names:
              - example1
              - example2
              - example3
            type: REQUEST_HEADERS

          - conditions:
              - lhs: VALUE
                op: RX
                rhs: "test"

              - lhs: SIZE
                op: LE
                rhs: "1000"
            names:
              - example1
              - example2
              - example3
            type: REQUEST_COOKIES

          - conditions:
              - lhs: SIZE
                op: EQ
                rhs: "1000"

              - lhs: VALUE
                op: CONTAINS
                rhs: "test-ansible"
            type: REQUEST_URI

          - conditions:
              - lhs: SIZE
                op: EQ
                rhs: "1000"

              - lhs: VALUE
                op: STARTS_WITH
                rhs: "test-ansible"
            type: QUERY_STRING
"""

RETURN = """
# The newly created app protection custom control resource record.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    validate_rules,
)
import json
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

def deep_equal(a, b):
    """
    Deep comparison of two structures (dicts, lists, or simple values).
    """
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if len(a) != len(b):
            return False
        for key in a:
            if key not in b or not deep_equal(a[key], b[key]):
                return False
    elif isinstance(a, list):
        if len(a) != len(b):
            return False
        for item_a, item_b in zip(a, b):
            if not deep_equal(item_a, item_b):
                return False
    else:
        return a == b
    return True

def normalize_app_custom_controls(control):
    """
    Normalize app protection profile data by setting computed values.
    """
    normalized = control.copy()

    computed_values = [
        "id",
        "creation_time",
        "modified_by",
        "modified_time",
        "action",
        "name",
        "description",
        "default_action",
        "paranoia_level",
        "severity",
        "control_rule_json",
        "protocol_type",
        "version",
        "rules",
        "type",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized

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
            "control_rule_json",
            "default_action",
            "default_action_value",
            "paranoia_level",
            "protocol_type",
            "rules",
            "severity",
            "type",
            "control_type",
        ]
    for param_name in params:
        control[param_name] = module.params.get(param_name, None)
    control_id = control.get("id", None)
    control_name = control.get("name", None)

    # Fetching existing control by ID or name
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

    # Normalize and compare existing and desired control data
    desired_control = normalize_app_custom_controls(control)
    current_control = normalize_app_custom_controls(existing_control) if existing_control else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_control.items():
        if key not in fields_to_exclude:
            if not deep_equal(current_control.get(key), value):
                differences_detected = True
                module.warn(f"Difference detected in {key}. Current: {current_control.get(key)}, Desired: {value}")

    # Validate the desired control values
    try:
        validate_rules(desired_control)
    except ValueError as ve:
        module.fail_json(msg=str(ve))

    # Check if default_action_value is provided when default_action is set to REDIRECT.
    default_action_value = control.get("default_action_value", None)
    default_action = control.get("default_action", None)
    if default_action == "REDIRECT" and not default_action_value:
        module.fail_json(msg="The default_action_value parameter is mandatory when default_action is set to REDIRECT.")

    if existing_control is not None:
        id = existing_control.get("id")
        existing_control.update(control)
        existing_control["id"] = id

    if state == "present":
        if existing_control is not None and differences_detected:
            """Update"""
            existing_control = {
                "control_id": existing_control.get("id", None),
                "name": existing_control.get("name", None),
                "description": existing_control.get("description", None),
                "action_value": existing_control.get("action_value", None),
                "control_rule_json": existing_control.get("control_rule_json", None),
                "control_type": existing_control.get("control_type", None),
                "default_action": existing_control.get("default_action", None),
                "default_action_value": existing_control.get(
                    "default_action_value", None
                ),
                "paranoia_level": existing_control.get("paranoia_level", None),
                "protocol_type": existing_control.get("protocol_type", None),
                "rules": existing_control.get("rules", None),
                "severity": existing_control.get("severity", None),
                "type": existing_control.get("type", None),
            }
            cleaned_control = deleteNone(existing_control)
            existing_control = client.inspection.update_custom_control(
                **cleaned_control
            )
            module.exit_json(changed=True, data=existing_control)

        elif existing_control is None:
            """Create"""
            new_control = {
                "name": control.get("name", None),
                "description": control.get("description", None),
                "action_value": control.get("action_value", None),
                "associated_inspection_profile_names": control.get(
                    "associated_inspection_profile_names", None
                ),
                "control_rule_json": control.get("control_rule_json", None),
                "control_type": control.get("control_type", None),
                "default_action": control.get("default_action", None),
                "default_action_value": control.get("default_action_value", None),
                "paranoia_level": control.get("paranoia_level", None),
                "protocol_type": control.get("protocol_type", None),
                "rules": control.get("rules", None),
                "severity": control.get("severity", None),
                "type": control.get("type", None),
            }
            cleaned_control = deleteNone(new_control)
            created_control = client.inspection.add_custom_control(**cleaned_control)
            module.exit_json(
                changed=True, data=created_control
            )  # Mark as changed since we are creating
        else:
            module.exit_json(
                changed=False, data=existing_control
            )  # If there's no change, exit without updating
    elif state == "absent" and existing_control is not None:
        code = client.inspection.delete_custom_control(
            control_id=existing_control.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_control)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str"),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
        action_value=dict(type="str", required=False),
        control_rule_json=dict(type="str", required=False),
        control_type=dict(
            type="str",
            required=False,
            choices=[
                "WEBSOCKET_PREDEFINED",
                "WEBSOCKET_CUSTOM",
                "THREATLABZ",
                "CUSTOM",
                "PREDEFINED",
            ],
        ),
        default_action=dict(type="str", required=False, choices=["PASS", "BLOCK", "REDIRECT"]),
        default_action_value=dict(type="str", required=False),
        paranoia_level=dict(type="str", required=False, choices=["1", "2", "3", "4"]),
        protocol_type=dict(
            type="str",
            required=False,
            choices=["HTTP", "HTTPS", "FTP", "RDP", "SSH", "WEBSOCKET", "VNC", "NONE"],
        ),
        type=dict(type="str", required=False, choices=["REQUEST", "RESPONSE"]),
        severity=dict(
            type="str", required=False, choices=["CRITICAL", "ERROR", "WARNING", "INFO"]
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
                        op=dict(
                            type="str",
                            required=False,
                            choices=[
                                "RX",
                                "CONTAINS",
                                "STARTS_WITH",
                                "ENDS_WITH",
                                "EQ",
                                "LE",
                                "GE",
                            ],
                        ),
                        rhs=dict(type="str", required=False),
                    ),
                ),
                names=dict(type="list", elements="str", required=False),
                type=dict(
                    type="str",
                    required=False,
                    choices=[
                        "REQUEST_HEADERS",
                        "REQUEST_URI",
                        "QUERY_STRING",
                        "REQUEST_COOKIES",
                        "REQUEST_METHOD",
                        "REQUEST_BODY",
                        "RESPONSE_HEADERS",
                        "RESPONSE_BODY",
                        "WS_MAX_PAYLOAD_SIZE",
                        "WS_MAX_FRAGMENT_PER_MESSAGE",
                    ],
                ),
            ),
            required=False,
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    # Retrieve 'rules' parameter for validation
    custom_ctl_rules = module.params.get('rules')

    # If rules are provided, validate them
    if custom_ctl_rules:
        try:
            validate_rules({"rules": custom_ctl_rules, "type": module.params.get('type')})
        except ValueError as validation_error:
            module.fail_json(msg=str(validation_error))

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())

if __name__ == "__main__":
    main()
