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
notes:
    - Check mode is supported.
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
              - RISK_FACTOR_TYPE
              - CHROME_ENTERPRISE
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
import json
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions,
    validate_operand,
    normalize_policy,
    deleteNone,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    rule_id = module.params.get("id")
    rule_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    rule = {
        "id": module.params.get("id"),
        "microtenant_id": module.params.get("microtenant_id"),
        "name": module.params.get("name"),
        "description": module.params.get("description"),
        "action": module.params.get("action"),
        "rule_order": module.params.get("rule_order"),
        "custom_msg": module.params.get("custom_msg"),
        "app_connector_group_ids": module.params.get("app_connector_group_ids"),
        "app_server_group_ids": module.params.get("app_server_group_ids"),
        "conditions": module.params.get("conditions"),
    }

    # Validate operands
    for condition in rule.get("conditions") or []:
        for operand in condition.get("operands", []):
            validation_result = validate_operand(operand, module)
            if validation_result:
                module.fail_json(msg=validation_result)

    existing_rule = None
    if rule_id:
        result, _, error = client.policies.get_rule(
            policy_type="access", rule_id=rule_id, query_params=query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving rule with id {rule_id}: {to_native(error)}"
            )
        existing_rule = result.as_dict()
        module.warn(f"Fetched existing rule: {existing_rule}")
    else:
        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules("access", query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(msg=f"Error listing access rules: {to_native(error)}")
        if error:
            module.fail_json(msg=f"Error listing access rules: {to_native(error)}")
        for r in rules_list:
            if r.name == rule_name:
                existing_rule = r.as_dict()
                break

    desired = normalize_policy(
        {**rule, "conditions": map_conditions(rule.get("conditions", []))}
    )

    if existing_rule:
        existing_rule["conditions"] = map_conditions(
            existing_rule.get("conditions", [])
        )
        current = normalize_policy(existing_rule)
        current["rule_order"] = str(existing_rule.get("order", ""))
    else:
        current = {}

    differences_detected = False
    for key in desired:
        if key in ["id", "policy_type"]:
            continue

        desired_value = desired.get(key)
        current_value = current.get(key)

        # Normalize None vs empty list
        if isinstance(desired_value, list) and not desired_value:
            desired_value = []
        if isinstance(current_value, list) and not current_value:
            current_value = []

        if str(desired_value) != str(current_value):
            differences_detected = True
            module.warn(
                f"Drift detected in '{key}': desired=({type(desired_value).__name__}) "
                f"{desired_value} | current=({type(current_value).__name__}) {current_value}"
            )

        if key == "conditions":
            module.warn(f"→ Desired: {json.dumps(desired_value, indent=2)}")
            module.warn(f"→ Current: {json.dumps(current_value, indent=2)}")

    # Reorder if specified
    if existing_rule and rule.get("rule_order"):
        current_order = str(existing_rule.get("order", ""))
        desired_order = str(rule["rule_order"])
        if desired_order != current_order:
            try:
                _, _, error = client.policies.reorder_rule(
                    policy_type="access",
                    rule_id=existing_rule["id"],
                    rule_order=desired_order,
                )
                if error:
                    module.fail_json(msg=f"Error reordering rule: {to_native(error)}")
                module.warn(f"Reordered rule to order {desired_order}")
            except Exception as e:
                module.fail_json(msg=f"Failed to reorder rule: {to_native(e)}")

    if module.check_mode:
        if state == "present" and (not existing_rule or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_rule:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    # Update or create
    if state == "present":
        if existing_rule and differences_detected:
            """Update"""
            update_data = deleteNone(
                {
                    "rule_id": existing_rule["id"],
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "action": rule["action"],
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "app_connector_group_ids": rule["app_connector_group_ids"],
                    "app_server_group_ids": rule["app_server_group_ids"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Update payload to SDK: {update_data}")
            result, _, error = client.policies.update_access_rule(**update_data)
            if error:
                module.fail_json(msg=f"Error updating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        elif not existing_rule:
            """Create"""
            create_data = deleteNone(
                {
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "action": rule["action"],
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "app_connector_group_ids": rule["app_connector_group_ids"],
                    "app_server_group_ids": rule["app_server_group_ids"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Create payload to SDK: {create_data}")
            result, _, error = client.policies.add_access_rule(**create_data)
            if error:
                module.fail_json(msg=f"Error creating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        else:
            module.exit_json(changed=False, data=existing_rule)

    elif state == "absent" and existing_rule:
        _, _, error = client.policies.delete_rule(
            policy_type="access", rule_id=existing_rule["id"]
        )
        if error:
            module.fail_json(msg=f"Error deleting rule: {to_native(error)}")
        module.exit_json(changed=True, data=existing_rule)

    module.exit_json(changed=False)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
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
                                "RISK_FACTOR_TYPE",
                                "CHROME_ENTERPRISE",
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
                    "RISK_FACTOR_TYPE",
                    "CHROME_ENTERPRISE",
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
