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
module: zpa_policy_credential_access_rule
short_description: Create Privileged Credential Rule
description:
  - This module create/update/delete Create Privileged Credential Rule
author:
  - William Guilherme (@willguibr)
version_added: "2.0.0"
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
    description: "The unique identifier of the policy rule."
    type: str
    required: false
  name:
    type: str
    required: true
    description:
      - The name of the Privileged Credential Rule
  description:
    description:
      - This is the description of the Privileged Credential Rule
    type: str
    required: false
  policy_type:
    description: "The value for differentiating policy types."
    type: str
    required: false
  rule_order:
    description: "The policy evaluation order number of the rule."
    type: str
    required: false
  operator:
    description:
      - This denotes the operation type.
    type: str
    required: false
    choices:
      - AND
      - OR
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
        choices: ["AND", "OR"]
      operands:
        description: "The various policy criteria. Array of attributes (e.g., object_type, lhs, rhs, name)"
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
- name: "Policy Isolation Rule - Example"
  zscaler.zpacloud.zpa_policy_access_isolation_rule:
    provider: "{{ zpa_cloud }}"
    name: "Policy Isolation Rule - Example"
    description: "Policy Isolation Rule - Example"
    rule_order: 1
    operator: "AND"
    zpn_isolation_profile_id: "216196257331286656"
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
# The newly created policy credential access rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    map_conditions_v2,
    normalize_policy_v2,
    validate_operand_v2,
    convert_conditions_v1_to_v2,
    collect_all_items,
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
import json


def core(module):
    state = module.params.get("state", "present")
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
        "credential": module.params.get("credential"),
        "credential_pool": module.params.get("credential_pool"),
        "conditions": module.params.get("conditions"),
    }

    module.warn(f"[core] Input rule: {json.dumps(rule, indent=2)}")

    for condition in rule.get("conditions") or []:
        for operand in condition.get("operands", []):
            validation_result = validate_operand_v2(operand, module)
            if validation_result:
                module.fail_json(msg=validation_result)

    existing_rule = None
    if rule_id:
        result, _, error = client.policies.get_rule(
            policy_type="credential", rule_id=rule_id, query_params=query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving rule with id {rule_id}: {to_native(error)}"
            )
        existing_rule = result.as_dict()
        # module.warn(f"Fetched existing rule: {existing_rule}")
        module.warn(f"[core] Existing rule from ID: {json.dumps(existing_rule, indent=2)}")
    else:
        module.warn("[core] Listing rules to match by name...")
        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules("credential", query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(msg=f"Error listing credential rules: {to_native(error)}")
        for r in rules_list:
            if r.name == rule_name:
                existing_rule = r.as_dict()
                break

    module.warn("[core] Normalizing desired state...")
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

    module.warn(f"[core] Normalized desired: {json.dumps(desired, indent=2)}")
    module.warn(f"[core] Normalized current: {json.dumps(current, indent=2)}")

    differences_detected = False
    for key in desired:
        if key in ["id", "policy_type"]:
            continue

        desired_value = desired.get(key)
        current_value = current.get(key)

        if isinstance(desired_value, list) and not desired_value:
            desired_value = []
        if isinstance(current_value, list) and not current_value:
            current_value = []

        if str(desired_value) != str(current_value):
            differences_detected = True
            module.warn(
                f"Drift detected in '{key}': desired=({type(desired_value).__name__}) {desired_value} | "
                f"current=({type(current_value).__name__}) {current_value}"
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
                    policy_type="credential",
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
                    "credential": rule["credential"],
                    "credential_pool": rule["credential_pool"],
                    "conditions": map_conditions_v2(rule["conditions"]),
                }
            )
            module.warn(f"[core] Update data before credential unpack: {json.dumps(update_data, indent=2)}")
            credential_id = None
            credential_pool_id = None

            credential = update_data.pop("credential", {})
            credential_pool = update_data.pop("credential_pool", {})

            if isinstance(credential, dict):
                credential_id = credential.get("id")

            if isinstance(credential_pool, dict):
                credential_pool_id = credential_pool.get("id")

            if credential_id and credential_pool_id:
                module.fail_json(
                    msg="Only one of 'credential' or 'credential_pool' may be specified."
                )
            elif not credential_id and not credential_pool_id:
                module.fail_json(
                    msg="You must specify either 'credential.id' or 'credential_pool.id'."
                )

            update_data["credential_id"] = credential_id
            update_data["credential_pool_id"] = credential_pool_id

            name = update_data.pop("name")
            module.warn(f"[core] Invoking update SDK with: {json.dumps(update_data, indent=2)}")
            result, _, error = client.policies.update_privileged_credential_rule_v2(
                rule_id=update_data.pop("rule_id"),
                name=name,
                **update_data,
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
                    "credential": rule["credential"],
                    "credential_pool": rule["credential_pool"],
                    "conditions": map_conditions_v2(rule["conditions"]),
                }
            )

            credential_id = None
            credential_pool_id = None

            credential = create_data.pop("credential", {})
            credential_pool = create_data.pop("credential_pool", {})

            if isinstance(credential, dict):
                credential_id = credential.get("id")

            if isinstance(credential_pool, dict):
                credential_pool_id = credential_pool.get("id")

            if credential_id and credential_pool_id:
                module.fail_json(
                    msg="Only one of 'credential' or 'credential_pool' may be specified."
                )
            elif not credential_id and not credential_pool_id:
                module.fail_json(
                    msg="You must specify either 'credential.id' or 'credential_pool.id'."
                )

            create_data["credential_id"] = credential_id
            create_data["credential_pool_id"] = credential_pool_id

            name = create_data.pop("name")
            conditions = create_data.pop("conditions", [])

            module.warn(f"[core] Invoking create SDK with: name={name}, credential_id={credential_id}, credential_pool_id={credential_pool_id}")
            module.warn(f"[core] Conditions payload: {json.dumps(conditions, indent=2)}")
            module.warn(f"[core] Create body: {json.dumps(create_data, indent=2)}")

            result, _, error = client.policies.add_privileged_credential_rule_v2(
                name=name,
                conditions=conditions,
                **create_data,
            )

            if error:
                module.fail_json(msg=f"Error creating rule: {to_native(error)}")
            module.exit_json(changed=True, data=result.as_dict())

        else:
            module.exit_json(changed=False, data=existing_rule)

    elif state == "absent" and existing_rule:
        _, _, error = client.policies.delete_rule(
            policy_type="credential", rule_id=existing_rule["id"]
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
        action=dict(type="str", required=False, default="INJECT_CREDENTIALS"),
        description=dict(type="str", required=False),
        policy_type=dict(type="str", required=False),
        operator=dict(type="str", required=False, choices=["AND", "OR"]),
        rule_order=dict(type="str", required=False),
        credential=dict(
            type="dict",
            required=False,
            options=dict(
                id=dict(type="str", required=False),
            ),
        ),
        credential_pool=dict(
            type="dict",
            required=False,
            options=dict(
                id=dict(type="str", required=False),
            ),
        ),
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

    # Example: SCIM-group specific object type enforcement
    conditions = module.params["conditions"]
    if conditions:
        valid_object_types = [
            "CONSOLE",
            "SAML",
            "SCIM",
            "SCIM_GROUP",
        ]
        for condition in conditions:
            for operand in condition.get("operands", []):
                object_type = operand.get("object_type", "").upper()
                if not object_type:
                    module.fail_json(msg="object_type is required in every operand.")
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
