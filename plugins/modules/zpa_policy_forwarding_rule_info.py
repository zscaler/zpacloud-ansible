#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_policy_forwarding_rule_info
short_description: Retrieves policy forwarding rule information.
description:
  - This module will allow the retrieval of information about a policy forwarding rule.
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
  name:
    description:
      - Name of the policy forwarding rule.
    required: false
    type: str
  id:
    description:
      - ID of the policy forwarding rule.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All Policy Forwarding Rules
  zscaler.zpacloud.zpa_policy_forwarding_rule_info:

- name: Get information About Forwarding Rules by Name
  zscaler.zpacloud.zpa_policy_forwarding_rule_info:
    name: "All Other Services"

- name: Get information About Forwarding Rules by ID
  zscaler.zpacloud.zpa_policy_forwarding_rule_info:
    id: "216196257331292020"
"""

RETURN = """
# Returns information on a specified policy forwarding rule.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
    deleteNone,
)


def core(module):
    policy_rule_name = module.params.get("name", None)
    policy_rule_id = module.params.get("id", None)
    client = ZPAClientHelper(module)
    policy_rules = []
    if policy_rule_id is not None:
        policy_rule = client.policies.get_rule(
            policy_type="client_forwarding", rule_id=policy_rule_id
        )
        if policy_rule is None:
            module.fail_json(msg="Failed to retrieve policy rule ID: '%s'" % (id))
        policy_rules = [policy_rule]
    elif policy_rule_name is not None:
        rules = client.policies.list_rules(policy_type="client_forwarding").to_list()
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
        policy_rules = client.policies.list_rules(
            policy_type="client_forwarding"
        ).to_list()
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
