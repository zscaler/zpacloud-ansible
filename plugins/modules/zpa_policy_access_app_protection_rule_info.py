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
module: zpa_policy_access_app_protection_rule_info
short_description: Retrieves App Protection Access Rule information.
description:
  - This module will allow the retrieval of information about a App Protection Access Rule.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
options:
  name:
    description:
      - Name of the App Protection Access Rule.
    required: false
    type: str
  id:
    description:
      - ID of the App Protection Access Rule.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All App Protection Access Rules
  zscaler.zpacloud.zpa_policy_access_app_protection_rule_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a App Protection Access Rule by Name
  zscaler.zpacloud.zpa_policy_access_app_protection_rule_info:
    provider: "{{ zpa_cloud }}"
    name: "App Protection Access Rule - Example"

- name: Get Details of a App Protection Access Rule by ID
  zscaler.zpacloud.zpa_policy_access_app_protection_rule_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291979"
"""

RETURN = """
# Returns information on a specified App Protection Access Rule.
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
            policy_type="inspection", rule_id=policy_rule_id
        )
        if policy_rule is None:
            module.fail_json(
                msg="Failed to retrieve app protection rule ID: '%s'" % (id)
            )
        policy_rules = [policy_rule]
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="inspection").to_list()
        found = False
        for rule in rules:
            if rule.get("name") == policy_rule_name:
                policy_rules = [rule]
                found = True
                break
        if not found:
            module.fail_json(
                msg="Failed to retrieve app protection rule Name: '%s'"
                % (policy_rule_name)
            )
    else:
        policy_rules = client.policies.list_rules(policy_type="inspection").to_list()
    module.exit_json(changed=False, data=policy_rules)


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
