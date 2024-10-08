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


def core(module):
    policy_rule_name = module.params.get("name", None)
    policy_rule_id = module.params.get("id", None)
    client = ZPAClientHelper(module)
    policy_rules = []
    if policy_rule_id is not None:
        policy_rule = client.policies.get_rule(
            policy_type="access", rule_id=policy_rule_id
        )
        if policy_rule is None:
            module.fail_json(msg="Failed to retrieve policy rule ID: '%s'" % (id))
        policy_rules = [policy_rule]
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="access").to_list()
        found = False
        for rule in rules:
            if rule.get("name") == policy_rule_name:
                policy_rules = [rule]
                found = True
                break
        if not found:
            module.fail_json(
                msg="Failed to retrieve policy rule Name: '%s'" % (policy_rule_name)
            )
    else:
        policy_rules = client.policies.list_rules(policy_type="access").to_list()
    module.exit_json(changed=False, policy_rules=policy_rules)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
