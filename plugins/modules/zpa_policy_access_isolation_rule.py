#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_policy_access_isolation_rule
short_description: Create a Policy Isolation Rule
description:
  - This module create/update/delete a Policy Isolation Rule in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
  - zscaler.zpacloud.fragments.state
options:
  action:
    description:
      - This is for providing the rule action.
    type: str
    required: false
    choices:
      - ISOLATE
      - BYPASS_ISOLATE
  id:
    description: ""
    type: str
    required: false
  policy_type:
    description: ""
    type: str
    required: false
  rule_order:
    description: ""
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
  description:
    description:
      - This is the description of the access policy.
    type: str
    required: false
  zpn_isolation_profile_id:
    description:
      - The isolation profile ID associated with the rule.
    type: str
    required: true
  name:
    type: str
    required: true
    description:
      - The name of the isolation rule.
  conditions:
    type: list
    elements: dict
    required: false
    description: "This is for providing the set of conditions for the policy"
    suboptions:
      negated:
        description: ""
        type: bool
        required: false
      operator:
        description: "The operation type. Supported values: AND, OR"
        type: str
        required: false
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
            required: True
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
    action: "ISOLATE"
    rule_order: 1
    operator: "AND"
    zpn_isolation_profile_id: "216196257331286656"
    conditions:
      - negated: false
        operator: "OR"
        operands:
          - object_type: "APP"
            lhs: "id"
            rhs: "216196257331292105"
          - object_type: "APP_GROUP"
            lhs: "id"
            rhs: "216196257331292103"
      - negated: false
        operator: "OR"
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
        "action",
        "operator",
        "rule_order",
        "zpn_isolation_profile_id",
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
            policy_type="isolation", rule_id=policy_rule_id
        )
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="isolation").to_list()
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
                "policy_type": "isolation",
                "rule_id": existing_policy.get("id", None),
                "name": existing_policy.get("name", None),
                "description": existing_policy.get("description", None),
                "action": existing_policy.get("action", "").upper()
                if existing_policy.get("action")
                else None,
                "zpn_isolation_profile_id": existing_policy.get(
                    "zpn_isolation_profile_id", None
                ),
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
                "zpn_isolation_profile_id": policy.get(
                    "zpn_isolation_profile_id", None
                ),
                "conditions": map_conditions(policy.get("conditions", [])),
            }
            module.warn(
                "zpn_isolation_profile_id: {policy.get('zpn_isolation_profile_id', None)}"
            )
            cleaned_policy = deleteNone(new_policy)
            created_policy = client.policies.add_isolation_rule(**cleaned_policy)
            module.exit_json(changed=True, data=created_policy)
        else:
            module.exit_json(changed=False, data=existing_policy)
    elif state == "absent" and existing_policy:
        code = client.policies.delete_rule(
            policy_type="isolation", rule_id=existing_policy.get("id")
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
        zpn_isolation_profile_id=dict(type="str", required=False),
        policy_type=dict(type="str", required=False),
        action=dict(
            type="str",
            required=False,
            choices=["ISOLATE", "isolate", "BYPASS_ISOLATE", "bypass_isolate"],
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
                        lhs=dict(type="str", required=True),
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
