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
module: zpa_policy_access_rule_reorder
short_description: Triggers the reorder of all policy types.
description:
  - This module will allow for the reorder of all supported policy types.
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
  - zscaler.zpacloud.fragments.modified_state

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
      - redirection
      - credential
      - capabilities
  rules:
    type: list
    elements: dict
    required: true
    description: "Contains a list of rule_ids to be reordered with its respective orders."
    suboptions:
      id:
        description: "ID of the rule to be reordered."
        type: str
        required: true
      order:
        description: "The order number of a new or existing rule to be reorder."
        type: str
        required: true
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)
    policy_type = module.params["policy_type"]
    desired_rules = module.params["rules"]
    microtenant_id = module.params.get("microtenant_id")
    state = module.params["state"]

    if state != "present":
        module.fail_json(
            msg="Invalid state. Only 'present' is supported for this module."
        )

    try:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

        rules_list, error = collect_all_items(
            lambda qp: client.policies.list_rules(policy_type, query_params=qp),
            query_params,
        )
        if error:
            module.fail_json(
                msg=f"Error listing {policy_type} rules: {to_native(error)}"
            )

        current_rules_order = {
            rule["id"]: idx + 1 for idx, rule in enumerate(rules_list)
        }

        # Check if current order matches desired
        is_order_correct = all(
            current_rules_order.get(rule["id"]) == int(rule["order"])
            for rule in desired_rules
        )
        if is_order_correct:
            module.exit_json(
                changed=False, msg="Rules are already in the desired order"
            )

        # Sort rules and validate
        desired_rules.sort(key=lambda x: int(x["order"]))
        orders = [int(rule["order"]) for rule in desired_rules]

        if min(orders) <= 0:
            module.fail_json(msg="Rule order must be greater than 0")

        duplicates = set(o for o in orders if orders.count(o) > 1)
        if duplicates:
            dup_ids = [r["id"] for r in desired_rules if int(r["order"]) in duplicates]
            module.fail_json(
                msg=f"Duplicate order(s) {', '.join(map(str, duplicates))} found in rule IDs: {', '.join(dup_ids)}"
            )

        missing = set(range(min(orders), max(orders) + 1)) - set(orders)
        if missing:
            module.fail_json(
                msg=f"Missing rule order numbers: {', '.join(map(str, sorted(missing)))}"
            )

        # Extract ordered rule ID list
        rule_ids_ordered = [rule["id"] for rule in desired_rules]

        # Call SDK with microtenant_id
        _unused, _unused, error = client.policies.bulk_reorder_rules(
            policy_type=policy_type,
            rules_orders=rule_ids_ordered,
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error reordering rules: {to_native(error)}")

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
                "redirection",
                "credential",
                "capabilities",
            ],
        ),
        rules=dict(
            type="list",
            required=True,
            elements="dict",
            options=dict(
                id=dict(type="str", required=True),
                order=dict(type="str", required=True),
            ),
        ),
        state=dict(type="str", choices=["present"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
