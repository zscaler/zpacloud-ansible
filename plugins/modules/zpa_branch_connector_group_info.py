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
module: zpa_branch_connector_group_info
short_description: Retrieves Branch Connector Group information.
description:
    - This module will allow the retrieval of information about a Branch Connector Group.
    - Branch Connector Groups are used to group Branch Connectors for management purposes.
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
  id:
    description:
      - The unique identifier of the Branch Connector Group.
    required: false
    type: str
  name:
    description:
      - The name of the Branch Connector Group.
    required: false
    type: str
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All Branch Connector Groups
  zscaler.zpacloud.zpa_branch_connector_group_info:
    provider: "{{ zpa_cloud }}"

- name: Get Information About a Branch Connector Group by Name
  zscaler.zpacloud.zpa_branch_connector_group_info:
    provider: "{{ zpa_cloud }}"
    name: "Branch_Connector_Group01"

- name: Get Information About a Branch Connector Group by ID
  zscaler.zpacloud.zpa_branch_connector_group_info:
    provider: "{{ zpa_cloud }}"
    id: "216199618143442006"
"""

RETURN = r"""
groups:
  description: >-
    A list containing details about the Branch Connector Group(s).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Branch Connector Group.
      type: str
      sample: "216199618143442006"
    name:
      description: The name of the Branch Connector Group.
      type: str
      sample: "Branch_Connector_Group01"
    enabled:
      description: Whether the Branch Connector Group is enabled.
      type: bool
      sample: true
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
    client = ZPAClientHelper(module)

    group_id = module.params.get("id")
    group_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Fetch all branch connector groups
    groups, err = collect_all_items(
        client.branch_connector_group.list_branch_connector_groups, query_params
    )
    if err:
        module.fail_json(msg=f"Error listing branch connector groups: {to_native(err)}")

    # If neither id nor name specified, return all groups
    if not group_id and not group_name:
        all_groups = []
        for group in groups:
            group_dict = group.as_dict() if hasattr(group, "as_dict") else group
            all_groups.append(group_dict)
        module.exit_json(changed=False, groups=all_groups)

    # Search for specific group by id or name
    matched_group = None
    for group in groups:
        group_dict = group.as_dict() if hasattr(group, "as_dict") else group
        if group_id and group_dict.get("id") == group_id:
            matched_group = group_dict
            break
        if group_name and group_dict.get("name") == group_name:
            matched_group = group_dict
            break

    if not matched_group:
        module.fail_json(
            msg=f"Couldn't find any branch connector group with name '{group_name}' or id '{group_id}'"
        )

    module.exit_json(changed=False, groups=[matched_group])


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["id", "name"]],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
