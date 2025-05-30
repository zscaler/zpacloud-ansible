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
module: zpa_policy_access_timeout_rule_v2
short_description: Manage ZPA Access Timeout Policy Rules (v2)
description:
  - Create, update, or delete a ZPA Access Timeout Policy Rule using the v2 policy engine.
  - This rule defines reauthentication behavior based on user or application context.
version_added: "2.0.0"
author:
  - William Guilherme (@willguibr)
requirements:
  - Zscaler SDK Python (https://pypi.org/project/zscaler-sdk-python/)
notes:
  - Check mode is supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  id:
    description:
      - The unique identifier of the policy rule.
    type: str
    required: false

  name:
    description:
      - The name of the timeout policy rule.
    type: str
    required: true

  description:
    description:
      - A detailed description of the timeout policy rule.
    type: str
    required: false

  custom_msg:
    description:
      - Custom message shown to users upon session timeout or reauthentication.
    type: str
    required: false

  reauth_idle_timeout:
    description:
      - The idle timeout interval before requiring reauthentication.
      - Accepts values like C(10 minutes), C(1 hour), or C(never).
      - Minimum value is 10 minutes or 'never'.
    type: str
    required: false

  reauth_timeout:
    description:
      - The absolute timeout interval before requiring reauthentication.
      - Accepts values like C(10 minutes), C(1 hour), or C(never).
      - Minimum value is 10 minutes or 'never'.
    type: str
    required: false

  rule_order:
    description:
      - The evaluation order of the rule within the policy set.
    type: str
    required: false

  microtenant_id:
    description:
      - The identifier of the microtenant associated with the policy rule.
    type: str
    required: false

  conditions:
    description:
      - Defines the match conditions under which the rule is applied.
    type: list
    elements: dict
    required: false
    suboptions:
      operator:
        description:
          - Logical operator to join multiple operands.
        type: str
        choices: ["AND", "OR"]
        required: false

      operands:
        description:
          - List of operand objects used to evaluate the condition.
        type: list
        elements: dict
        required: false
        suboptions:
          object_type:
            description:
              - The type of the object to match.
            type: str
            choices:
              - APP
              - APP_GROUP
              - CLIENT_TYPE
              - IDP
              - POSTURE
              - PLATFORM
              - SAML
              - SCIM
              - SCIM_GROUP
            required: false

          values:
            description:
              - List of string values for the operand.
            type: list
            elements: str
            required: false

          entry_values:
            description:
              - Dictionary of LHS and RHS entries for advanced operands.
            type: dict
            required: false
            suboptions:
              lhs:
                description:
                  - Left-hand-side operand for comparison.
                type: str
                required: false
              rhs:
                description:
                  - Right-hand-side operand for comparison.
                type: str
                required: false
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
"""

RETURN = r"""
# The newly created policy access timeout rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
import json
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    normalize_policy_v2,
    map_conditions_v2,
    validate_operand_v2,
    convert_conditions_v1_to_v2,
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
        "rule_order": module.params.get("rule_order"),
        "reauth_timeout": module.params.get("reauth_timeout"),
        "reauth_idle_timeout": module.params.get("reauth_idle_timeout"),
        "conditions": module.params.get("conditions"),
    }

    # Validate operands
    for condition in rule.get("conditions") or []:
        for operand in condition.get("operands", []):
            validation_result = validate_operand_v2(operand, module)
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
        # module.warn("[core] Listing rules to match by name...")
        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules("timeout", query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(msg=f"Error listing timeout rules: {to_native(error)}")
        for r in rules_list:
            if r.name == rule_name:
                existing_rule = r.as_dict()
                break

    # module.warn("[core] Normalizing desired state...")
    desired = normalize_policy_v2(
        {**rule, "conditions": map_conditions_v2(rule.get("conditions", []))}
    )

    if existing_rule:
        existing_rule["conditions"] = convert_conditions_v1_to_v2(
            existing_rule.get("conditions", []), module=module
        )
        current = normalize_policy_v2(existing_rule)
    else:
        current = {}

    # module.warn(f"[core] Normalized desired: {json.dumps(desired, indent=2)}")
    # module.warn(f"[core] Normalized current: {json.dumps(current, indent=2)}")

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
            #     f"Drift detected in '{key}': desired=({type(desired_value).__name__}) {desired_value} | "
            #     f"current=({type(current_value).__name__}) {current_value}"
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
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "reauth_timeout": rule["reauth_timeout"],
                    "reauth_idle_timeout": rule["reauth_idle_timeout"],
                    "conditions": map_conditions_v2(rule["conditions"]),
                }
            )
            module.warn(f"Update payload to SDK: {update_data}")
            result, _unused, error = client.policies.update_timeout_rule_v2(
                **update_data
            )
            if error:
                module.fail_json(msg=f"Error updating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        elif not existing_rule:
            create_data = deleteNone(
                {
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "custom_msg": rule["custom_msg"],
                    "rule_order": rule["rule_order"],
                    "reauth_timeout": rule["reauth_timeout"],
                    "reauth_idle_timeout": rule["reauth_idle_timeout"],
                    "conditions": map_conditions_v2(rule["conditions"]),
                }
            )
            module.warn(f"Create payload to SDK: {create_data}")
            result, _unused, error = client.policies.add_timeout_rule_v2(**create_data)
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
                        values=dict(type="list", elements="str", required=False),
                        entry_values=dict(
                            type="dict",
                            required=False,
                            options=dict(
                                lhs=dict(type="str", required=False),
                                rhs=dict(type="str", required=False),
                            ),
                        ),
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

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
