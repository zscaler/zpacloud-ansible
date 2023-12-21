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
module: zpa_policy_access_forwarding_rule
short_description: Create a Policy Forwarding Rule.
description:
  - This module will create, update or delete a specific Policy Forwarding Rule
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
options:
  id:
    description: ""
    type: str
  name:
    description: ""
    type: str
    required: True
  description:
    description: ""
    type: str
    required: False
  action:
    description: ""
    type: str
    required: False
    choices: ["INTERCEPT", "INTERCEPT_ACCESSIBLE", "BYPASS"]
    default: INTERCEPT
  custom_msg:
    description: ""
    type: str
    required: False
  operator:
    description: ""
    type: str
    required: False
    choices: ["AND", "OR"]
  policy_type:
    description: ""
    type: str
    required: False
  rule_order:
    description: ""
    type: str
    required: False
  conditions:
    description: ""
    type: list
    elements: dict
    required: False
    suboptions:
      id:
        description: ""
        type: str
      negated:
        description: ""
        type: bool
        required: False
      operator:
        description: ""
        type: str
        required: True
        choices: ["AND", "OR"]
      operands:
        description: ""
        type: list
        elements: dict
        required: False
        suboptions:
          id:
            description: ""
            type: str
          idp_id:
            description: ""
            type: str
            required: False
          name:
            description: ""
            type: str
            required: False
          lhs:
            description: ""
            type: str
            required: True
          rhs:
            description: ""
            type: str
            required: False
          rhs_list:
            description: ""
            type: list
            elements: str
            required: False
          object_type:
            description: ""
            type: str
            required: True
            choices:
              [
                "APP",
                "APP_GROUP",
                "SAML",
                "IDP",
                "SCIM",
                "SCIM_GROUP",
                "CLIENT_TYPE",
                "TRUSTED_NETWORK",
                "MACHINE_GRP",
                "POSTURE",
                "EDGE_CONNECTOR_GROUP",
              ]
"""

EXAMPLES = """
- name: Policy Forwarding Rule - Example
  zscaler.zpacloud.zpa_policy_access_forwarding_rule:
    provider: "{{ zpa_cloud }}"
    name: "Policy Forwarding Rule - Example"
    description: "Policy Forwarding Rule - Example"
    action: "BYPASS"
    rule_order: 1
    operator: "AND"
    conditions:
      - negated: false
        operator: "OR"
        operands:
          - name: "app_segment"
            object_type: "APP"
            lhs: "id"
            rhs: "216196257331292105"
      - negated: false
        operator: "OR"
        operands:
          - name: "segment_group"
            object_type: "APP_GROUP"
            lhs: "id"
            rhs: "216196257331292103"
      - negated: false
        operator: "OR"
        operands:
          - name: "zpn_client_type_exporter"
            object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_exporter"
          - name: "zpn_client_type_browser_isolation"
            object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_browser_isolation"
          - name: "zpn_client_type_zapp"
            object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_zapp"
      - negated: false
        operator: "OR"
        operands:
          - name: "CrowdStrike_ZPA_ZTA_80"
            object_type: "POSTURE"
            lhs: "{{ postures.data[0].posture_udid }}"
            rhs: "false"
"""

RETURN = """
# The newly created access client forwarding policy rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions,
    validate_operand,
    normalize_policy,
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", "present")
    client = ZPAClientHelper(module)
    policy_rule_id = module.params.get("id", None)
    policy_rule_name = module.params.get("name", None)
    policy = dict()
    params = [
        "id",
        "name",
        "description",
        "policy_type",
        "action",
        "operator",
        "rule_order",
        "conditions",
    ]
    for param_name in params:
        policy[param_name] = module.params.get(param_name, None)

    conditions = module.params.get("conditions") or []

    # Validate each operand in the conditions
    for condition in conditions:
        operands = condition.get("operands", [])
        for operand in operands:
            validation_result = validate_operand(operand, module)
            if validation_result:
                module.fail_json(
                    msg=validation_result
                )  # Fail if validation returns a warning or error message

    existing_policy = None
    if policy_rule_id is not None:
        existing_policy = client.policies.get_rule(
            policy_type="client_forwarding", rule_id=policy_rule_id
        )
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="client_forwarding").to_list()
        for rule in rules:
            if rule.get("name") == policy_rule_name:
                existing_policy = rule
                break

    if existing_policy is not None:
        # Normalize both policies' conditions
        policy["conditions"] = map_conditions(policy.get("conditions", []))
        existing_policy["conditions"] = map_conditions(
            existing_policy.get("conditions", [])
        )

        desired_policy = normalize_policy(policy)
        current_policy = normalize_policy(existing_policy)

        fields_to_exclude = ["id", "policy_type"]
        differences_detected = False
        for key, value in desired_policy.items():
            if key not in fields_to_exclude and current_policy.get(key) != value:
                differences_detected = True
                module.warn(
                    f"Difference detected in {key}. Current: {current_policy.get(key)}, Desired: {value}"
                )

    if existing_policy is not None:
        id = existing_policy.get("id")
        existing_policy.update(policy)
        existing_policy["id"] = id

    if state == "present":
        if existing_policy is not None and differences_detected:
            """Update"""
            updated_policy = {
                "policy_type": "client_forwarding",
                "rule_id": existing_policy.get("id", None),
                "name": existing_policy.get("name", None),
                "description": existing_policy.get("description", None),
                "action": existing_policy.get("action", "").upper()
                if existing_policy.get("action")
                else None,
                "conditions": map_conditions(existing_policy.get("conditions", [])),
                "rule_order": existing_policy.get("rule_order", None),
            }
            cleaned_policy = deleteNone(updated_policy)
            updated_policy = client.policies.update_rule(**cleaned_policy)
            module.exit_json(changed=True, data=updated_policy)
        elif existing_policy is None:
            """Create"""
            new_policy = {
                "name": policy.get("name", None),
                "description": policy.get("description", None),
                "action": policy.get("action", "").upper()
                if policy.get("action")
                else None,
                "rule_order": policy.get("rule_order", None),
                "conditions": map_conditions(policy.get("conditions", [])),
            }
            cleaned_policy = deleteNone(new_policy)
            created_policy = client.policies.add_client_forwarding_rule(
                **cleaned_policy
            )
            module.exit_json(
                changed=True, data=created_policy
            )  # Mark as changed since we are creating
        else:
            module.exit_json(
                changed=False, data=existing_policy
            )  # If there's no change, exit without updating
    elif state == "absent" and existing_policy is not None:
        code = client.policies.delete_rule(
            policy_type="client_forwarding", rule_id=existing_policy.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_policy)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str"),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        policy_type=dict(type="str", required=False),
        action=dict(
            type="str",
            required=False,
            choices=[
                "bypass",
                "BYPASS",
                "intercept",
                "INTERCEPT",
                "intercept_accessible",
                "INTERCEPT_ACCESSIBLE",
            ],
        ),
        operator=dict(type="str", required=False, choices=["AND", "OR"]),
        rule_order=dict(type="str", required=False),
        conditions=dict(
            type="list",
            elements="dict",
            options=dict(
                id=dict(type="str"),
                negated=dict(type="bool", required=False),
                operator=dict(type="str", required=True, choices=["AND", "OR"]),
                operands=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str"),
                        idp_id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                        lhs=dict(type="str", required=False),
                        rhs=dict(type="str", required=False),
                        rhs_list=dict(type="list", elements="str", required=False),
                        object_type=dict(
                            type="str",
                            required=True,
                            choices=[
                                "APP",
                                "APP_GROUP",
                                "CLIENT_TYPE",
                                "BRANCH_CONNECTOR_GROUP",
                                "EDGE_CONNECTOR_GROUP",
                                "POSTURE",
                                "MACHINE_GRP",
                                "TRUSTED_NETWORK",
                                "PLATFORM",
                                "IDP",
                                "SAML",
                                "SCIM",
                                "SCIM_GROUP",
                            ],
                        ),
                    ),
                    required=False,
                ),
            ),
            required=False,
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    # Custom validation for object_type
    conditions = module.params["conditions"]
    if conditions:  # Add this check to handle when conditions is None
        for condition in conditions:
            operands = condition.get("operands", [])
            for operand in operands:
                object_type = operand.get("object_type")
                valid_object_types = [
                    "APP",
                    "APP_GROUP",
                    "CLIENT_TYPE",
                    "BRANCH_CONNECTOR_GROUP",
                    "EDGE_CONNECTOR_GROUP",
                    "POSTURE",
                    "MACHINE_GRP",
                    "TRUSTED_NETWORK",
                    "PLATFORM",
                    "IDP",
                    "SAML",
                    "SCIM",
                    "SCIM_GROUP",
                ]
                if (
                    object_type is None or object_type == ""
                ):  # Explicitly check for None or empty string
                    module.fail_json(
                        msg="object_type cannot be empty or None. Must be one of: {', '.join(valid_object_types)}"
                    )
                elif object_type not in valid_object_types:
                    module.fail_json(
                        msg="Invalid object_type: {object_type}. Must be one of: {', '.join(valid_object_types)}"
                    )
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
