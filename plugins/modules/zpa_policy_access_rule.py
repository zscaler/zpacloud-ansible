#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023, Zscaler, Inc
#
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
module: zpa_policy_access_rule
short_description: Create a Policy Access Rule
description:
  - This module create/update/delete a Policy Access Rule in the ZPA Cloud.
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
  action:
    description:
      - This is for providing the rule action.
    type: str
    required: false
    choices:
      - ALLOW
      - DENY
      - REQUIRE_APPROVAL
  id:
    type: str
    description: ""
  name:
    description:
      - This is the name of the policy.
    type: str
    required: True
  description:
    type: str
    description: "This is the description of the access rule"
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
  custom_msg:
    description:
      - This is for providing a customer message for the user
    type: str
    required: false
  conditions:
    type: list
    elements: dict
    required: False
    description: "This is for providing the set of conditions for the policy"
    suboptions:
      id:
        description: ""
        type: str
      negated:
        description: ""
        type: bool
        required: False
      operator:
        description: "This denotes the operation type"
        type: str
        required: True
        choices: ["AND", "OR"]
      operands:
        required: False
        description: "This signifies the various policy criteria"
        type: list
        elements: dict
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
            description:
              - This signifies the key for the object type
              - String ID example: "id"
            type: str
            required: True
          rhs:
            description:
              - This denotes the value for the given object type. Its value depends upon the key
              - For APP, APP_GROUP, and IDP, the supported value is entity id.
              - For CLIENT_TYPE, the supported values are zpn_client_type_zapp (for ZApp) and zpn_client_type_exporter (for Clientless).
              - For POSTURE, the supported values are: true (verified), false (verification failed).
              - For TRUSTED_NETWORK, the supported value is true.
            type: str
            required: False
          object_type:
            description:
              - This is for specifying the policy criteria
              - POSTURE and TRUSTED_NETWORK values are only supported for the CLIENT_TYPE.
            type: str
            required: True
            choices:
              - APP
              - APP_GROUP
              - SAML
              - IDP
              - CLIENT_TYPE
              - TRUSTED_NETWORK
              - MACHINE_GRP
              - POSTURE
              - SCIM
              - SCIM_GROUP
              - EDGE_CONNECTOR_GROUP
              - COUNTRY_CODE
              - PLATFORM
  state:
    description: "Whether the app should be present or absent."
    type: str
    choices:
        - present
        - absent
    default: present
"""

EXAMPLES = """
- name: Gather ID for Trusted Network Corp-Trusted-Networks
  zscaler.zpacloud.zpa_trusted_networks_info:
    name: Corp-Trusted-Networks
  register: network_id

- name: Gather ID for Posture Profiles CrowdStrike_ZPA_ZTA_40
  zscaler.zpacloud.zpa_posture_profile_info:
    name: CrowdStrike_ZPA_ZTA_40
  register: posture1

- name: Gather ID for Machine Group CrowdStrike_ZPA_ZTA_80
  zscaler.zpacloud.zpa_machine_group_info:
    name: Example MGR01
  register: machine_groups

- name: Gather ID for Segment Group Example100
  zscaler.zpacloud.zpa_segment_group_info:
    name: "Example100"
  register: segment_group

- name: Gather ID for App Segment app01
  zscaler.zpacloud.zpa_application_segment_info:
    name: "app01"
  register: app01

- name: Create/update/delete a policy rule
  zscaler.zpacloud.zpa_policy_access_rule:
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import map_conditions
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import validate_operand
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
    deleteNone,
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

    conditions = module.params.get('conditions', [])

    # Validate each operand in the conditions
    for condition in conditions:
        operands = condition.get('operands', [])
        for operand in operands:
            validation_result = validate_operand(operand, module)
            if validation_result:
                module.fail_json(msg=validation_result)  # Fail if validation returns a warning or error message


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
        id = existing_policy.get("id")
        existing_policy.update(policy)
        existing_policy["id"] = id
    if state == "present":
        if existing_policy is not None:
            """Update"""
            updated_policy = {
                "policy_type": "access",
                "rule_id": existing_policy.get("id", None),
                "name": existing_policy.get("name", None),
                "description": existing_policy.get("description", None),
                "rule_order": existing_policy.get("rule_order", None),
                "action": existing_policy.get("action", "").upper(),
                "conditions": map_conditions(existing_policy.get("conditions", [])),
                "custom_msg": existing_policy.get("custom_msg", None),
                "app_connector_group_ids": existing_policy.get("app_connector_group_ids", None),
                "app_server_group_ids": existing_policy.get("app_server_group_ids", None)
            }
            cleaned_policy = deleteNone(updated_policy)
            updated_policy = client.policies.update_access_rule(**cleaned_policy)
            module.exit_json(changed=True, data=updated_policy)
        else:
            """Create"""
            new_policy = {
                "name": policy.get("name", None),
                "description": policy.get("description", None),
                "action": policy.get("action", None),
                "rule_order": policy.get("rule_order", None),
                "conditions": map_conditions(policy.get("conditions", [])),
                "custom_msg": policy.get("custom_msg", None),
                "app_connector_group_ids": policy.get("app_connector_group_ids", None),
                "app_server_group_ids": policy.get("app_server_group_ids", None)
            }
            cleaned_policy = deleteNone(new_policy)
            created_policy = client.policies.add_access_rule(**cleaned_policy)
            module.exit_json(changed=True, data=created_policy)  # Mark as changed since we are creating
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
            type="str", required=False, choices=["allow", "deny", "ALLOW", "DENY", "REQUIRE_APPROVAL"]
        ),
        operator=dict(type="str", required=False, choices=["AND", "OR"]),
        rule_order=dict(type="str", required=False),
        conditions=dict(
            type="list",
            elements="dict",
            options=dict(
                id=dict(type="str", required=False),
                negated=dict(type="bool", required=False),
                operator=dict(type="str", required=False, choices=["AND", "OR"]),
                operands=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        id=dict(type="str", required=False),
                        idp_id=dict(type="str", required=False),
                        name=dict(type="str", required=False),
                        lhs=dict(type="str", required=True),
                        rhs=dict(type="str", required=False),
                        object_type=dict(
                            type="str",
                            required=True,
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
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
