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
module: zpa_policy_access_forwarding_rule
short_description: Create a Policy Forwarding Rule.
description:
  - This module will create, update or delete a specific Policy Forwarding Rule
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
    description: "The name of the forwarding rule"
    type: str
    required: True
  description:
    description: "The description of the forwarding rule"
    type: str
    required: False
  action:
    description: "The action of the forwarding rule"
    type: str
    required: False
    choices:
      - INTERCEPT
      - INTERCEPT_ACCESSIBLE
      - BYPASS
      - bypass
      - intercept
      - intercept_accessible
  rule_order:
    description: "The policy evaluation order number of the rule."
    type: str
    required: false
  operator:
    description: "Denotes the operation type. These are operands used between criteria"
    type: str
    required: false
    choices: ["AND", "OR"]
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
  conditions:
    description: "Specifies the set of conditions for the policy rule"
    type: list
    elements: dict
    required: false
    suboptions:
      operator:
        description: "The operator of the condition set"
        type: str
        required: True
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
                "PLATFORM",
                "BRANCH_CONNECTOR_GROUP",
                "EDGE_CONNECTOR_GROUP",
              ]
"""

EXAMPLES = r"""
- name: Policy Forwarding Rule - Example
  zscaler.zpacloud.zpa_policy_access_forwarding_rule:
    provider: "{{ zpa_cloud }}"
    name: "Policy Forwarding Rule - Example"
    description: "Policy Forwarding Rule - Example"
    action: "BYPASS"
    rule_order: 1
    operator: "AND"
    conditions:
      - operator: "OR"
        operands:
          - name: "app_segment"
            object_type: "APP"
            lhs: "id"
            rhs: "216196257331292105"
      - operator: "OR"
        operands:
          - name: "segment_group"
            object_type: "APP_GROUP"
            lhs: "id"
            rhs: "216196257331292103"
      - operator: "OR"
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
      - operator: "OR"
        operands:
          - name: "CrowdStrike_ZPA_ZTA_80"
            object_type: "POSTURE"
            lhs: "{{ postures.data[0].posture_udid }}"
            rhs: "false"
"""

RETURN = r"""
# The newly created access client forwarding policy rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions,
    validate_operand,
    normalize_policy,
    collect_all_items,
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
import json


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
            policy_type="client_forwarding", rule_id=rule_id, query_params=query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving rule with id {rule_id}: {to_native(error)}"
            )
        existing_rule = result.as_dict()
        module.warn(f"Fetched existing rule: {existing_rule}")
    else:
        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules("client_forwarding", query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(
                msg=f"Error listing client forwarding rules: {to_native(error)}"
            )
        if error:
            module.fail_json(
                msg=f"Error listing client forwardin rules: {to_native(error)}"
            )
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
                    policy_type="client_forwarding",
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
            """Update"""
            update_data = deleteNone(
                {
                    "rule_id": existing_rule["id"],
                    "microtenant_id": rule["microtenant_id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "action": rule["action"],
                    "rule_order": rule["rule_order"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Update payload to SDK: {update_data}")
            result, _unused, error = client.policies.update_client_forwarding_rule(
                **update_data
            )
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
                    "rule_order": rule["rule_order"],
                    "conditions": map_conditions(rule["conditions"]),
                }
            )
            module.warn(f"Create payload to SDK: {create_data}")
            result, _unused, error = client.policies.add_client_forwarding_rule(
                **create_data
            )
            if error:
                module.fail_json(msg=f"Error creating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        else:
            module.exit_json(changed=False, data=existing_rule)

    elif state == "absent" and existing_rule:
        _unused, _unused, error = client.policies.delete_rule(
            policy_type="client_forwarding", rule_id=existing_rule["id"]
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
        action=dict(
            type="str",
            required=False,
            choices=[
                "BYPASS",
                "INTERCEPT",
                "INTERCEPT_ACCESSIBLE",
                "bypass",
                "intercept",
                "intercept_accessible",
            ],
        ),
        operator=dict(type="str", required=False, choices=["AND", "OR"]),
        rule_order=dict(type="str", required=False),
        conditions=dict(
            type="list",
            elements="dict",
            options=dict(
                operator=dict(type="str", required=True, choices=["AND", "OR"]),
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

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
