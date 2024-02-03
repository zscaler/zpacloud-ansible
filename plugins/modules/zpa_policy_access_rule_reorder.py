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
module: zpa_policy_access_rule_reorder
short_description: Triggers the reorder of all policy types.
description:
  - This module will allow for the reorder of all supported policy types.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider

  - zscaler.zpacloud.fragments.state
options:
  policy_type:
    description:
      - The name of the supported policy types.
    required: true
    type: str
    choices:
      - access
      - timeout
      - client_forwarding
      - isolation
      - inspection
  rules:
    type: list
    elements: dict
    required: true
    description: "Contains a list of rule_ids to be reordered with its respective orders."
    suboptions:
      id:
        description: "ID of the rule to be reordered."
        type: str
      order:
        description: "The order number of a new or existing rule to be reorder."
        type: str
"""

EXAMPLES = """
    - name: Reorder Rules
      zscaler.zpacloud.zpa_policy_access_rule_reorder:
        provider: "{{ zpa_cloud }}"
        policy_type: "access"
        rules:
          - id: "216196257331369420"
            order: 1
          - id: "216196257331369421"
            order: 2
          - id: "216196257331369422"
            order: 3
"""

RETURN = """
# The newly created policy access rule reorder.
"""

import traceback
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    policy_type = module.params["policy_type"]
    desired_rules = module.params["rules"]

    try:
        # Fetch the current rules and their order
        current_rules = client.policies.list_rules(policy_type)
        current_rules_order = {rule["id"]: idx + 1 for idx, rule in enumerate(current_rules)}

        # Check if the current order matches the desired order
        is_order_correct = all(
            current_rules_order.get(rule["id"]) == rule["order"] for rule in desired_rules
        )

        # If the current order is already as desired, exit without changes
        if is_order_correct:
            module.exit_json(changed=False, msg="Rules are already in the desired order")

        # Sort rules by order
        desired_rules.sort(key=lambda x: x["order"])

        # Validate rules (e.g., check for duplicates, order > 0, etc.)
        orders = [rule["order"] for rule in desired_rules]
        if min(orders) <= 0:
            module.fail_json(msg="New order of rule should be greater than 0")

        order_count = {}
        for order in orders:
            order_count[order] = order_count.get(order, 0) + 1
        duplicate_orders = [order for order, count in order_count.items() if count > 1]
        if duplicate_orders:
            duplicate_rules = [
                str(rule["id"]) for rule in desired_rules if rule["order"] in duplicate_orders
            ]
            module.fail_json(
                msg=f"Duplicate order '{duplicate_orders[0]}' used by rules with IDs: {', '.join(duplicate_rules)}"
            )

        # Check for gaps in rule orders
        expected_orders = set(range(min(orders), max(orders) + 1))
        actual_orders = set(orders)
        missing_orders = expected_orders - actual_orders
        if missing_orders:
            module.fail_json(
                msg=f"Missing rule order numbers: {', '.join(map(str, sorted(missing_orders)))}"
            )

        # Prepare the rules orders for bulk reorder
        rules_orders = {rule["id"]: rule["order"] for rule in desired_rules}

        # Call reorder method from SDK
        client.policies.bulk_reorder_rules(policy_type, rules_orders)

        module.exit_json(changed=True, msg="Reordered successfully")

    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())

def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        policy_type=dict(
            type="str",
            required=True,
            choices=[
                "access",
                "timeout",
                "client_forwarding",
                "isolation",
                "inspection",
            ],
        ),
        rules=dict(
            type="list",
            required=True,
            elements="dict",
            options=dict(
                id=dict(type="str", required=True),
                order=dict(type="int", required=True),
            ),
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

if __name__ == "__main__":
    main()