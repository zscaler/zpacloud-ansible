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
module: zpa_policy_forwarding_rule
short_description: Create a Policy Forwarding Rule.
description:
  - This module will create, update or delete a specific Policy Forwarding Rule
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
options:
  client_id:
    description: ""
    required: false
    type: str
  client_secret:
    description: ""
    required: false
    type: str
  customer_id:
    description: ""
    required: false
    type: str
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
  default_rule:
    description: ""
    type: bool
    required: False
  default_rule_name:
    description: ""
    type: str
    required: False
  custom_msg:
    description: ""
    type: str
    required: False
  bypass_default_rule:
    description: ""
    type: bool
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
  priority:
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
  state:
    description: ""
    type: str
    choices: ["present", "absent"]
    default: present
"""

EXAMPLES = """
- name: Policy Forwarding Rule - Example
  zscaler.zpacloud.zpa_policy_forwarding_rule:
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
    deleteNone,
)


def map_conditions(conditions_obj):
    result = []
    for condition in conditions_obj:
        operands = condition.get("operands")
        if operands is not None and isinstance(operands, list):
            for op in operands:
                if (
                    op.get("object_type", None) is not None
                    and op.get("lhs", None) is not None
                    and op.get("rhs", None) is not None
                ):
                    operand = (
                        op.get("object_type", None),
                        op.get("lhs", None),
                        op.get("rhs", None),
                    )
                    result.append(operand)
    return result


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
        "policy_type",
        "action",
        "operator",
        "rule_order",
        "conditions",
    ]
    for param_name in params:
        policy[param_name] = module.params.get(param_name, None)
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
        id = existing_policy.get("id")
        existing_policy.update(policy)
        existing_policy["id"] = id
    if state == "present":
        if existing_policy is not None:
            """Update"""
            existing_policy = deleteNone(
                dict(
                    policy_type="client_forwarding",
                    rule_id=existing_policy.get("id", None),
                    name=existing_policy.get("name", None),
                    description=existing_policy.get("description", None),
                    action=existing_policy.get("action", "").upper(),
                    conditions=map_conditions(existing_policy.get("conditions", [])),
                )
            )
            existing_policy = client.policies.update_rule(**existing_policy)
            module.exit_json(changed=True, data=existing_policy)
        else:
            """Create"""
            policy = deleteNone(
                dict(
                    name=policy.get("name", None),
                    description=policy.get("description", None),
                    action=policy.get("action", None),
                    conditions=map_conditions(policy.get("conditions", [])),
                )
            )
            policy = client.policies.add_client_forwarding_rule(**policy)
            module.exit_json(changed=False, data=policy)
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
    id_name_spec = dict(
        type="list",
        elements="dict",
        options=dict(
            id=dict(type="str", required=True), name=dict(type="str", required=False)
        ),
        required=False,
    )
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
                        lhs=dict(type="str", required=True),
                        rhs=dict(type="str", required=False),
                        rhs_list=dict(type="list", elements="str", required=False),
                        object_type=dict(
                            type="str",
                            required=True,
                            choices=[
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
                            ],
                        ),
                    ),
                    required=False,
                ),
            ),
            required=False,
        ),
        app_server_groups=id_name_spec,
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
