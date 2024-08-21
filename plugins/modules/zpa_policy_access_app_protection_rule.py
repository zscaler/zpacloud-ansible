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
module: zpa_policy_access_app_protection_rule
short_description: Create a Policy App Protection Rule in the ZPA Cloud.
description:
  - This module create/update/delete a Policy Isolation Rule in the ZPA Cloud.
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
    description: "The unique identifier of the policy rule"
    type: str
    required: false
  name:
    type: str
    required: true
    description:
      - The name of the isolation rule.
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
      - INSPECT
      - BYPASS_INSPECT
      - inspect
      - bypass_inspect
  rule_order:
    description: "The policy evaluation order number of the rule."
    type: str
    required: false
  policy_type:
    description: "Indicates the policy type. The following value is supported: client_forwarding"
    type: str
    required: false
  operator:
    description:
      - Denotes the operation type
      - These are operands used between criteria
    type: str
    required: false
    choices:
      - AND
      - OR
  zpn_inspection_profile_id:
    description:
      - The isolation profile ID associated with the rule.
    type: str
    required: false
  conditions:
    type: list
    elements: dict
    required: false
    description: "This is for providing the set of conditions for the policy"
    suboptions:
      operator:
        description: "The operation type. Supported values: AND, OR"
        type: str
        required: false
        choices:
          - AND
          - OR
      operands:
        description: "The various policy criteria. Array of attributes (e.g., objectType, lhs, rhs, name)"
        type: list
        elements: dict
        required: false
        suboptions:
          idp_id:
            description: "The ID information for the Identity Provider (IdP)"
            type: str
            required: false
          lhs:
            description: "The key for the object type. String ID example: id"
            type: str
            required: false
          rhs:
            description: >
                - The value for the given object type. Its value depends upon the key
                - For APP, APP_GROUP, and IDP, the supported value is entity id
                - For CLIENT_TYPE, the supported values are: zpn_client_type_zapp (for Zscaler Client Connector), zpn_client_type_exporter (for Clientless)
                - For POSTURE, the supported values are: true (verified), false (verification failed)
                - For TRUSTED_NETWORK, the supported value is true
            type: str
            required: false
          object_type:
            description: >
              - This is for specifying the policy criteria
              - Supported values: APP, APP_GROUP, SAML, IDP, CLIENT_TYPE, POSTURE, TRUSTED_NETWORK, MACHINE_GRP, SCIM, SCIM_GROUP.
              - POSTURE and TRUSTED_NETWORK values are only supported for the CLIENT_TYPE.
            type: str
            required: false
"""

EXAMPLES = """
- name: "Policy App Protection Rule - Example"
  zscaler.zpacloud.zpa_policy_access_app_protection_rule:
    provider: "{{ zpa_cloud }}"
    name: "Policy App Protection Rule - Example"
    description: "Policy App Protection Rule"
    rule_order: 1
    action: "INSPECT"
    operator: "AND"
    zpn_inspection_profile_id: "216196257331286656"
    conditions:
      - operator: "OR"
        operands:
          - object_type: "APP"
            lhs: "id"
            rhs: "216196257331292105"
          - object_type: "APP_GROUP"
            lhs: "id"
            rhs: "216196257331292103"
      - operator: "OR"
        operands:
          - name:
            object_type: "CLIENT_TYPE"
            lhs: "id"
            rhs: "zpn_client_type_zapp"
"""

RETURN = """
# The newly created policy access isolation rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions,
    normalize_policy,
    validate_operand,
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
        "rule_order",
        "action",
        "operator",
        "zpn_inspection_profile_id",
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
            policy_type="inspection", rule_id=policy_rule_id
        )
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="inspection").to_list()
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

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_policy is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_policy is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_policy is not None:
        id = existing_policy.get("id")
        existing_policy.update(policy)
        existing_policy["id"] = id

    if state == "present":
        if existing_policy is not None and differences_detected:
            """Update"""
            updated_policy = {
                "policy_type": "inspection",
                "rule_id": existing_policy.get("id", None),
                "name": existing_policy.get("name", None),
                "description": existing_policy.get("description", None),
                "rule_order": existing_policy.get("rule_order", None),
                "action": (
                    existing_policy.get("action", "").upper()
                    if existing_policy.get("action")
                    else None
                ),
                "zpn_inspection_profile_id": existing_policy.get(
                    "zpn_inspection_profile_id", None
                ),
                "conditions": map_conditions(existing_policy.get("conditions", [])),
            }

            cleaned_policy = deleteNone(updated_policy)
            updated_policy = client.policies.update_rule(**cleaned_policy)
            module.exit_json(changed=True, data=updated_policy)
        elif existing_policy is None:
            """Create"""
            new_policy = {
                "name": policy.get("name", None),
                "description": policy.get("description", None),
                "rule_order": policy.get("rule_order", None),
                "action": (
                    policy.get("action", "").upper() if policy.get("action") else None
                ),
                "zpn_inspection_profile_id": policy.get(
                    "zpn_inspection_profile_id", None
                ),
                "conditions": map_conditions(policy.get("conditions", [])),
            }
            module.warn(
                "zpn_inspection_profile_id: {policy.get('zpn_inspection_profile_id', None)}"
            )
            cleaned_policy = deleteNone(new_policy)
            created_policy = client.policies.add_app_protection_rule(**cleaned_policy)
            module.exit_json(changed=True, data=created_policy)
        else:
            module.exit_json(changed=False, data=existing_policy)
    elif state == "absent" and existing_policy:
        code = client.policies.delete_rule(
            policy_type="inspection", rule_id=existing_policy.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_policy)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        zpn_inspection_profile_id=dict(type="str", required=False),
        policy_type=dict(type="str", required=False),
        action=dict(
            type="str",
            required=False,
            choices=["INSPECT", "inspect", "BYPASS_INSPECT", "bypass_inspect"],
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
                    "EDGE_CONNECTOR_GROUP",
                    "POSTURE",
                    "TRUSTED_NETWORK",
                    "PLATFORM",
                    "IDP",
                    "SAML",
                    "SCIM",
                    "SCIM_GROUP",
                    "MACHINE_GRP",
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
