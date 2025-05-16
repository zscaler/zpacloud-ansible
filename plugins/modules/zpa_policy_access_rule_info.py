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
module: zpa_policy_access_rule_info
short_description: Retrieves policy access rule information.
description:
  - This module will allow the retrieval of information about a policy access rule.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
      - Name of the policy rule.
    required: false
    type: str
  id:
    description:
      - ID of the policy rule.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All Policy Access Rules
  zscaler.zpacloud.zpa_policy_access_rule_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Policy Access Rule by Name
  zscaler.zpacloud.zpa_policy_access_rule_facts:
    provider: "{{ zpa_cloud }}"
    name: "Policy Access Rule - Example"

- name: Get Details of a Policy Access Rule by ID
  zscaler.zpacloud.zpa_policy_access_rule_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291979"
"""

RETURN = """
# Returns information on a specified Policy Access Rule.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    policy_rule_id = module.params.get("id")
    policy_rule_name = module.params.get("name")
    policy_type = module.params.get("policy_type")
    microtenant_id = module.params.get("microtenant_id")

    client = ZPAClientHelper(module)

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Retrieve rule by ID
    if policy_rule_id:
        result, _, error = client.policies.get_rule(
            policy_type=policy_type, rule_id=policy_rule_id, query_params=query_params
        )
        if error or not result:
            module.fail_json(
                msg=f"Failed to retrieve policy rule ID '{policy_rule_id}' for type '{policy_type}'"
            )
        module.exit_json(
            changed=False,
            data=[result.as_dict() if hasattr(result, "as_dict") else result],
        )

    # Retrieve all rules using pagination
    rules, err = collect_all_items(
        lambda qp: client.policies.list_rules(policy_type=policy_type, query_params=qp),
        query_params,
    )
    if err:
        module.fail_json(
            msg=f"Error retrieving policy rules for type '{policy_type}': {to_native(err)}"
        )

    # Optionally filter by name using getattr()
    if policy_rule_name:
        match = next(
            (r for r in rules if getattr(r, "name", None) == policy_rule_name), None
        )
        if not match:
            available = [getattr(r, "name", "") for r in rules]
            module.fail_json(
                msg=f"Policy rule '{policy_rule_name}' not found. Available: {available}"
            )
        rules = [match]

    module.exit_json(
        changed=False, data=[r.as_dict() if hasattr(r, "as_dict") else r for r in rules]
    )


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
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
                "siem",
                "portal_policy",
                "vpn_policy",
            ],
        ),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
