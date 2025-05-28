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
module: zpa_segment_group_info
short_description: Retrieves information about a segment group.
description:
    - This module will allow the retrieval of information about a segment group.
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
     - Name of the server group.
    required: false
    type: str
  id:
    description:
     - ID of the server group.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Detail Information of All Segment Groups
  zscaler.zpacloud.zpa_segment_group_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Segment Group by Name
  zscaler.zpacloud.zpa_segment_group_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example"

- name: Get Details of a Segment Group by ID
  zscaler.zpacloud.zpa_segment_group_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
groups:
  description: >-
    A list of dictionaries containing details about the segment groups.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the segment group.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the segment group.
      type: str
      sample: "Example200"
    description:
      description: A brief description of the segment group.
      type: str
      sample: "Example200"
    enabled:
      description: Indicates whether the segment group is enabled.
      type: bool
      sample: true
    config_space:
      description: The configuration space where the segment group resides.
      type: str
      sample: "DEFAULT"
    microtenant_name:
      description: The name of the microtenant associated with the segment group.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the segment group.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the segment group was last modified.
      type: str
      sample: "1724111641"
    creation_time:
      description: The timestamp when the segment group was created.
      type: str
      sample: "1724111641"
    policy_migrated:
      description: Indicates if the policy associated with the segment group has been migrated.
      type: bool
      sample: true
    tcp_keep_alive_enabled:
      description: Indicates whether TCP keep-alive is enabled for the segment group.
      type: bool
      sample: false
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

    if group_id:
        result, _unused, error = client.segment_groups.get_group(group_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Segment Group ID '{group_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, groups=[result.as_dict()])

    # If no ID, we fetch all
    group_list, err = collect_all_items(client.segment_groups.list_groups, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving Segment Groups: {to_native(err)}")

    result_list = [g.as_dict() for g in group_list]

    if group_name:
        matched = next((g for g in result_list if g.get("name") == group_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Segment Group '{group_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, groups=result_list)


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
