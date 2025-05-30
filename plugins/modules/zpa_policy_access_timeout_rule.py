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

DOCUMENTATION = r"""
---
module: zpa_policy_access_timeout_rule
short_description: Create a Policy Timeout Rule
description:
  - This module create/update/delete a Policy Timeout Rule in the ZPA Cloud.
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
    description: "The unique identifier of the policy set"
    type: str
  name:
    type: str
    required: True
    description:
      - This is the name of the timeout policy.
  description:
    description:
      - This is the description of the access policy.
    type: str
    required: false
  action:
    description:
      - This is for providing the rule action.
    type: str
    required: false
    choices:
      - RE_AUTH
  rule_order:
    description: "The policy evaluation order number of the rule."
    type: str
    required: false
  custom_msg:
    description:
      - This is for providing a customer message for the user.
    type: str
    required: false
  reauth_idle_timeout:
    type: str
    required: false
    description:
      - The reauthentication idle timeout
      - Use minute, minutes, hour, hours, day, days, or never.
      - Timeout interval must be at least 10 minutes or 'never.
      - i.e 10 minutes, 1 hour, 2 hours, or never
  reauth_timeout:
    type: str
    required: false
    description:
      - The reauthentication timeout.
      - Use minute, minutes, hour, hours, day, days, or never.
      - Timeout interval must be at least 10 minutes or 'never.
      - i.e 10 minutes, 1 hour, 2 hours, or never
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
  conditions:
    type: list
    elements: dict
    required: False
    description: "Specifies the set of conditions for the policy rule"
    suboptions:
      operator:
        description: "The operator of the condition set"
        type: str
        required: false
        choices: ["AND", "OR"]
      operands:
        description: "The operands of the condition set"
        type: list
        elements: dict
        required: false
        suboptions:
          idp_id:
            description: "The unique identifier of the IdP"
            type: str
            required: false
          lhs:
            description: "The key for the object type"
            type: str
            required: false
          rhs:
            description: "The value for the given object type. Its value depends upon the key"
            type: str
            required: false
          object_type:
            description: "The object type of the operand"
            type: str
            required: false
            choices:
              - APP
              - APP_GROUP
              - CLIENT_TYPE
              - SAML
              - IDP
              - SCIM
              - SCIM_GROUP
              - POSTURE
              - PLATFORM

"""

EXAMPLES = r"""
- name: "Policy Timeout Rule - Example"
  zscaler.zpacloud.zpa_policy_access_timeout_rule:
    provider: "{{ zpa_cloud }}"
    name: "Policy Timeout Rule - Example"
    description: "Policy Timeout Rule - Example"
    action: "RE_AUTH"
    rule_order: 1
    reauth_idle_timeout: '1 day'
    reauth_timeout: '10 days'
    operator: "AND"
    conditions:
      - operator: "OR"
        operands:
          - object_type: "APP"
            lhs: "id"
            rhs: "216196257331292105"
      - operator: "OR"
        operands:
          - object_type: "APP_GROUP"
            lhs: "id"
            rhs: "216196257331292103"
      - operator: "AND"
        operands:
          - object_type: "PLATFORM"
            lhs: ios
            rhs: "true"
          - object_type: "PLATFORM"
            lhs: linux
            rhs: "true"
          - object_type: "PLATFORM"
            lhs: windows
            rhs: "true"
      - operator: "OR"
        operands:
          - object_type: "SCIM_GROUP"
            lhs: "72058304855015574"
            rhs: "490880"
            idp_id: "72058304855015574"
          - object_type: "SCIM_GROUP"
            lhs: "72058304855015574"
            rhs: "490877"
            idp_id: "72058304855015574"
      - operator: "AND"
        operands:
          - object_type: "SCIM"
            lhs: "72058304855015576"
            rhs: "Smith"
            idp_id: "72058304855015574"
      - operator: "AND"
        operands:
          - object_type: "SAML"
            lhs: "72058304855021553"
            rhs: "jdoe@acme.com"
            idp_id: "72058304855015574"
      - operator: "OR"
        operands:
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_exporter"
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_browser_isolation"
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_zapp"
      - operator: "OR"
        operands:
          - object_type: "POSTURE"
            lhs: "13ba3d97-aefb-4acc-9e54-6cc230dee4a5"
            rhs: "true"
      - operator: "AND"
        operands:
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_exporter"
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_zapp_partner"
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_browser_isolation"
          - object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_zapp"
"""

RETURN = r"""
# The newly created policy access timeout rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
import json
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions,
    normalize_policy,
    validate_operand,
    validate_timeout_intervals,
    collect_all_items,
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", "present")
    client = ZPAClientHelper(module)

    rule_id = module.params.get("id")
    rule_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Fetch parameters conditionally based on state
    if state != "absent":  # Only process reauth times if not deleting the policy
        reauth_idle_timeout = module.params.get("reauth_idle_timeout")
        reauth_timeout = module.params.get("reauth_timeout")

        # Validate and convert timeout intervals
        reauth_idle_timeout_seconds, error = validate_timeout_intervals(
            reauth_idle_timeout
        )
        if error:
            module.fail_json(msg=error)
        reauth_timeout_seconds, error = validate_timeout_intervals(reauth_timeout)
        if error:
            module.fail_json(msg=error)

        # Assign converted values back to params to be used in API calls or other logic
        module.params["reauth_idle_timeout"] = reauth_idle_timeout_seconds
        module.params["reauth_timeout"] = reauth_timeout_seconds
    else:
        # Set default values for deletion case where these values aren't needed
        module.params["reauth_idle_timeout"] = None
        module.params["reauth_timeout"] = None

    rule = {
        "id": module.params.get("id"),
        "microtenant_id": module.params.get("microtenant_id"),
        "name": module.params.get("name"),
        "description": module.params.get("description"),
        "custom_msg": module.params.get("custom_msg"),
        "action": module.params.get("action"),
        "rule_order": module.params.get("rule_order"),
        "reauth_timeout": module.params.get("reauth_timeout"),
        "reauth_idle_timeout": module.params.get("reauth_idle_timeout"),
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
        result, _unused, error = client.policies.get_rule(
            policy_type="timeout", rule_id=rule_id, query_params=query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving rule with id {rule_id}: {to_native(error)}"
            )
        existing_rule = result.as_dict()
        module.warn(f"Fetched existing rule: {existing_rule}")
    else:
        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules("timeout", query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(msg=f"Error listing timeout rules: {to_native(error)}")
        if error:
            module.fail_json(msg=f"Error listing timeout rules: {to_native(error)}")
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
            # module.warn(
            #     f"Drift detected in '{key}': desired=({type(desired_value).__name__}) "
            #     f"{desired_value} | current=({type(current_value).__name__}) {current_value}"
            # )

        if key == "conditions":
            module.warn(f"→ Desired: {json.dumps(desired_value, indent=2)}")
            module.warn(f"→ Current: {json.dumps(current_value, indent=2)}")

    # Reorder if specified
    if existing_rule and rule.get("rule_order"):
        current_order = str(existing_rule.get("order", ""))
        desired_order = str(rule["rule_order"])
        if desired_order != current_order:
            try:
                _unused, _unused, error = client.policies.reorder_rule(
                    policy_type="timeout",
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
            module.exit_json(changed=False, data=existing_rule or {})

    # Update or create
    if state == "present":
        if existing_rule and differences_detected:
            update_data = deleteNone(
                {
                    "rule_id": existing_rule["id"],
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "action": rule["action"],
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "reauth_timeout": rule["reauth_timeout"],
                    "reauth_idle_timeout": rule["reauth_idle_timeout"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Update payload to SDK: {update_data}")
            result, _unused, error = client.policies.update_timeout_rule(**update_data)
            if error:
                module.fail_json(msg=f"Error updating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        elif not existing_rule:
            create_data = deleteNone(
                {
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "action": rule["action"],
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "reauth_timeout": rule["reauth_timeout"],
                    "reauth_idle_timeout": rule["reauth_idle_timeout"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Create payload to SDK: {create_data}")
            result, _unused, error = client.policies.add_timeout_rule(**create_data)
            if error:
                module.fail_json(msg=f"Error creating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        else:
            module.exit_json(changed=False, data=existing_rule)

    elif state == "absent" and existing_rule:
        _unused, _unused, error = client.policies.delete_rule(
            policy_type="timeout", rule_id=existing_rule["id"]
        )
        if error:
            module.fail_json(msg=f"Error deleting rule: {to_native(error)}")
        module.exit_json(changed=True, data=existing_rule)

    module.exit_json(changed=False, data=existing_rule or {})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        custom_msg=dict(type="str", required=False),
        action=dict(type="str", required=False, choices=["RE_AUTH"]),
        reauth_idle_timeout=dict(type="str", required=False),
        reauth_timeout=dict(type="str", required=False),
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
                                "CLIENT_TYPE",
                                "IDP",
                                "POSTURE",
                                "PLATFORM",
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
                    "IDP",
                    "POSTURE",
                    "PLATFORM",
                    "SAML",
                    "SCIM",
                    "SCIM_GROUP",
                ]
                if (
                    object_type is None or object_type == ""
                ):  # Explicitly check for None or empty string
                    module.fail_json(
                        msg=f"object_type cannot be empty or None. Must be one of: {', '.join(valid_object_types)}"
                    )
                elif object_type not in valid_object_types:
                    module.fail_json(
                        msg=f"Invalid object_type: {object_type}. Must be one of: {', '.join(valid_object_types)}"
                    )
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
