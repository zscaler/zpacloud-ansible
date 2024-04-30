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
module: zpa_policy_access_rule
short_description: Create a Policy Access Rule
description:
  - This module create/update/delete a Policy Access Rule in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  action:
    description:
      - This is for providing the rule action.
    type: str
    required: false
    choices:
      - ALLOW
      - DENY
      - REQUIRE_APPROVAL
      - allow
      - deny
      - require_approval
  id:
    type: str
    description: "The unique identifier of the policy rule."
  name:
    description:
      - This is the name of the policy.
    type: str
    required: True
  description:
    type: str
    description: "This is the description of the access rule"
  policy_type:
    description: "The value for differentiating policy types."
    type: str
  rule_order:
    description: "The policy evaluation order number of the rule."
    type: str
  operator:
    description:
      - This denotes the operation type.
    type: str
    choices:
      - AND
      - OR
  custom_msg:
    description:
      - This is for providing a customer message for the user.
    type: str
  app_connector_group_ids:
    description:
      - List of App Connector Group IDs.
    type: list
    elements: str
  app_server_group_ids:
    description:
      - List of Server Group IDs.
    type: list
    elements: str
  conditions:
    description: "This is for providing the set of conditions for the policy."
    type: list
    elements: dict
    suboptions:
      operator:
        description: "This denotes the operation type."
        type: str
        choices: ["AND", "OR"]
      operands:
        description: "This signifies the various policy criteria."
        type: list
        elements: dict
        suboptions:
          idp_id:
            description: "The unique identifier of the IdP."
            type: str
          lhs:
            description: "This signifies the key for the object type."
            type: str
          rhs:
            description: "This denotes the value for the given object type."
            type: str
          object_type:
            description: "This is for specifying the policy criteria."
            type: str
            choices:
              - APP
              - APP_GROUP
              - LOCATION
              - IDP
              - SAML
              - SCIM
              - SCIM_GROUP
              - CLIENT_TYPE
              - POSTURE
              - TRUSTED_NETWORK
              - BRANCH_CONNECTOR_GROUP
              - EDGE_CONNECTOR_GROUP
              - MACHINE_GRP
              - COUNTRY_CODE
              - PLATFORM
"""

EXAMPLES = """
- name: Gather ID for Trusted Network Corp-Trusted-Networks
  zscaler.zpacloud.zpa_trusted_networks_facts:
    provider: "{{ zpa_cloud }}"
    name: Corp-Trusted-Networks
  register: network_id

- name: Gather ID for Posture Profiles CrowdStrike_ZPA_ZTA_40
  zscaler.zpacloud.zpa_posture_profile_facts:
    provider: "{{ zpa_cloud }}"
    name: CrowdStrike_ZPA_ZTA_40
  register: posture1

- name: Gather ID for Machine Group CrowdStrike_ZPA_ZTA_80
  zscaler.zpacloud.zpa_machine_group_facts:
    provider: "{{ zpa_cloud }}"
    name: Example MGR01
  register: machine_groups

- name: Gather ID for Segment Group Example100
  zscaler.zpacloud.zpa_segment_group_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example100"
  register: segment_group

- name: Gather ID for App Segment app01
  zscaler.zpacloud.zpa_application_segment_facts:
    provider: "{{ zpa_cloud }}"
    name: "app01"
  register: app01

- name: Create/update/delete a policy rule
  zscaler.zpacloud.zpa_policy_access_rule:
    provider: "{{ zpa_cloud }}"
    name: "Ansible_Access_Policy_Rule"
    description: "Ansible_Access_Policy_Rule"
    action: "ALLOW"
    rule_order: 1
    app_connector_group_ids:
      - "216196257331368721"
      - "216196257331368838"
    app_server_group_ids:
      - "216196257331368722"
      - "216196257331368839"
    operator: "AND"
    conditions:
      - operator: "AND"
        negated: false
        operands:
          - object_type: "TRUSTED_NETWORK"
            lhs: "{{ network_id.data[0].network_id }}"
            rhs: "true"
      - operator: "OR"
        negated: false
        operands:
          - object_type: "POSTURE"
            lhs: "{{ posture1.data[0].posture_udid }}"
            rhs: "true"
      - operator: "AND"
        negated: false
        operands:
          - object_type: "COUNTRY_CODE"
            lhs: "CA"
            rhs: "true"
      - operator: "AND"
        negated: false
        operands:
          - object_type: "MACHINE_GRP"
            lhs: "id"
            rhs: "{{ machine_groups.data[0].id }}"
      - operator: "AND"
        negated: false
        operands:
          - object_type: "APP_GROUP"
            lhs: "id"
            rhs: "{{ segment_group.data[0].id }}"
          - object_type: "APP"
            lhs: "id"
            rhs: "{{ app01.data[0].id }}"
"""

RETURN = """
# The newly created policy access rule resource record.
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
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    policy_rule_id = module.params.get("id", None)
    policy_rule_name = module.params.get("name", None)
    policy = dict()
    params = [
        "id",
        "name",
        "description",
        "action",
        "rule_order",
        "policy_type",
        "custom_msg",
        "app_connector_group_ids",
        "app_server_group_ids",
        "operator",
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
            policy_type="access", rule_id=policy_rule_id
        )
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="access").to_list()
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
                # module.warn(
                #     f"Difference detected in {key}. Current: {current_policy.get(key)}, Desired: {value}"
                # )

    if existing_policy:
        desired_order = policy.get("rule_order")
        current_order = str(existing_policy.get("order", ""))
        if desired_order and desired_order != current_order:
            try:
                reordered_policy = client.policies.reorder_rule(
                    policy_type="client_forwarding",
                    rule_id=existing_policy["id"],
                    rule_order=desired_order,
                )
                if reordered_policy:
                    module.warn("Reordered rule to new order: {}".format(desired_order))
                else:
                    module.fail_json(msg="Failed to reorder rule, no policy returned.")
            except Exception as e:
                module.fail_json(msg="Failed to reorder rule: {}".format(str(e)))

    if existing_policy is not None:
        id = existing_policy.get("id")
        existing_policy.update(policy)
        existing_policy["id"] = id

    if state == "present":
        if existing_policy is not None and differences_detected:
            """Update"""
            updated_policy = {
                "policy_type": "access",
                "rule_id": existing_policy.get("id", None),
                "name": existing_policy.get("name", None),
                "description": existing_policy.get("description", None),
                "rule_order": existing_policy.get("rule_order", None),
                "action": (
                    existing_policy.get("action", "").upper()
                    if existing_policy.get("action")
                    else None
                ),
                "conditions": map_conditions(existing_policy.get("conditions", [])),
                "custom_msg": existing_policy.get("custom_msg", None),
                "app_connector_group_ids": existing_policy.get(
                    "app_connector_group_ids", None
                ),
                "app_server_group_ids": existing_policy.get(
                    "app_server_group_ids", None
                ),
            }
            cleaned_policy = deleteNone(updated_policy)
            updated_policy = client.policies.update_access_rule(**cleaned_policy)
            module.exit_json(changed=True, data=updated_policy)
        elif existing_policy is None:
            """Create"""
            new_policy = {
                "name": policy.get("name", None),
                "description": policy.get("description", None),
                "action": (
                    policy.get("action", "").upper() if policy.get("action") else None
                ),
                "rule_order": policy.get("rule_order", None),
                "conditions": map_conditions(policy.get("conditions", [])),
                "custom_msg": policy.get("custom_msg", None),
                "app_connector_group_ids": policy.get("app_connector_group_ids", None),
                "app_server_group_ids": policy.get("app_server_group_ids", None),
            }
            cleaned_policy = deleteNone(new_policy)
            created_policy = client.policies.add_access_rule(**cleaned_policy)
            module.exit_json(
                changed=True, data=created_policy
            )  # Mark as changed since we are creating
        else:
            module.exit_json(
                changed=False, data=existing_policy
            )  # If there's no change, exit without updating
    elif state == "absent" and existing_policy is not None:
        code = client.policies.delete_rule(
            policy_type="access", rule_id=existing_policy.get("id")
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
        custom_msg=dict(type="str", required=False),
        app_connector_group_ids=dict(type="list", elements="str", required=False),
        app_server_group_ids=dict(type="list", elements="str", required=False),
        action=dict(
            type="str",
            required=False,
            choices=[
                "ALLOW",
                "DENY",
                "REQUIRE_APPROVAL",
                "allow",
                "deny",
                "require_approval",
            ],
        ),
        operator=dict(type="str", required=False, choices=["AND", "OR"]),
        rule_order=dict(type="str", required=False),
        conditions=dict(
            type="list",
            elements="dict",
            options=dict(
                operator=dict(type="str", required=False, choices=["AND", "OR"]),
                operands=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        idp_id=dict(type="str", required=False),
                        lhs=dict(type="str", required=False),
                        rhs=dict(type="str", required=False),
                        object_type=dict(
                            type="str",
                            required=False,
                            choices=[
                                "APP",
                                "APP_GROUP",
                                "LOCATION",
                                "IDP",
                                "SAML",
                                "SCIM",
                                "SCIM_GROUP",
                                "CLIENT_TYPE",
                                "POSTURE",
                                "TRUSTED_NETWORK",
                                "BRANCH_CONNECTOR_GROUP",
                                "EDGE_CONNECTOR_GROUP",
                                "MACHINE_GRP",
                                "COUNTRY_CODE",
                                "PLATFORM",
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
                    "LOCATION",
                    "IDP",
                    "SAML",
                    "SCIM",
                    "SCIM_GROUP",
                    "CLIENT_TYPE",
                    "POSTURE",
                    "TRUSTED_NETWORK",
                    "BRANCH_CONNECTOR_GROUP",
                    "EDGE_CONNECTOR_GROUP",
                    "MACHINE_GRP",
                    "COUNTRY_CODE",
                    "PLATFORM",
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
