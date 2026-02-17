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
module: zpa_workload_tag_group_info
short_description: Retrieves information about a Workload Tag Group.
description:
    - This module will allow the retrieval of information about a Workload Tag Group.
    - Workload Tag Groups are used to organize and categorize workloads within ZPA.
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
     - Name of the Workload Tag Group.
    required: false
    type: str
  id:
    description:
     - ID of the Workload Tag Group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Detail Information of All Workload Tag Groups
  zscaler.zpacloud.zpa_workload_tag_group_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Workload Tag Group by Name
  zscaler.zpacloud.zpa_workload_tag_group_info:
    provider: "{{ zpa_cloud }}"
    name: "Production"

- name: Get Details of a Workload Tag Group by ID
  zscaler.zpacloud.zpa_workload_tag_group_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
groups:
  description: >-
    A list of dictionaries containing details about the Workload Tag Groups.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Workload Tag Group.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the Workload Tag Group.
      type: str
      sample: "Production"
    enabled:
      description: Indicates whether the Workload Tag Group is enabled.
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

    query_params = {}

    if group_id:
        # Get all workload tag groups and find the one with matching ID
        group_list, err = collect_all_items(
            client.workload_tag_group.get_workload_tag_group_summary, query_params
        )
        if err:
            module.fail_json(
                msg=f"Error retrieving Workload Tag Groups: {to_native(err)}"
            )

        result_list = [g.as_dict() for g in group_list]
        matched = next((g for g in result_list if g.get("id") == group_id), None)

        if not matched:
            module.fail_json(msg=f"Workload Tag Group ID '{group_id}' not found.")
        module.exit_json(changed=False, groups=[matched])

    # If no ID, we fetch all
    group_list, err = collect_all_items(
        client.workload_tag_group.get_workload_tag_group_summary, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving Workload Tag Groups: {to_native(err)}")

    result_list = [g.as_dict() for g in group_list]

    if group_name:
        matched = next((g for g in result_list if g.get("name") == group_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Workload Tag Group '{group_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, groups=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
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
