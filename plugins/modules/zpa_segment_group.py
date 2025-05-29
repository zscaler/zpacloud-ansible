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
module: zpa_segment_group
short_description: Create a Segment Group
description:
    - This module will create/update/delete a segment group resource.
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
  - zscaler.zpacloud.fragments.state

options:
  id:
    description: "The unique identifier of the Segment Group"
    type: str
    required: false
  name:
    description: "Name of the segment group"
    type: str
    required: true
  description:
    description: "Description of the segment group"
    type: str
    required: false
  enabled:
    description: "Whether this segment group is enabled or not"
    type: bool
    required: false
    default: true
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Create/Update/Delete a Segment Group
  zscaler.zpacloud.zpa_segment_group:
    provider: "{{ zpa_cloud }}"
    name: Example Segment Group
    description: Example Segment Group
    enabled: true
"""

RETURN = """
# The newly created segment group resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    normalize_app,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect parameters
    params = ["id", "name", "description", "enabled", "microtenant_id"]
    group = {param: module.params.get(param) for param in params}
    group_id = group.get("id")
    group_name = group.get("name")
    microtenant_id = group.get("microtenant_id")

    # Step 1: Fetch existing group if possible
    existing_group = None
    if group_id:
        result, _unused, error = client.segment_groups.get_group(
            group_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving group by ID {group_id}: {to_native(error)}"
            )
        if result:
            existing_group = result.as_dict()

    elif group_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        group_list, error = collect_all_items(
            client.segment_groups.list_groups, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing segment groups: {to_native(error)}")
        for item in group_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == group_name:
                existing_group = item_dict
                break

    # Step 2: Normalize and compare
    desired_group = normalize_app(group)
    current_group = normalize_app(existing_group) if existing_group else {}

    fields_to_ignore = ["id"]

    drift = any(
        desired_group.get(k) != current_group.get(k)
        for k in desired_group
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_group))
            or (state == "absent" and existing_group)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_group:
            if drift:
                update_group = deleteNone(
                    {
                        "group_id": existing_group.get("id"),
                        "microtenant_id": desired_group.get("microtenant_id"),
                        "name": desired_group.get("name"),
                        "description": desired_group.get("description"),
                        "enabled": desired_group.get("enabled"),
                    }
                )
                updated, _unused, error = client.segment_groups.update_group_v2(
                    group_id=update_group.pop("group_id"), **update_group
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating segment group: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_group)
        else:
            payload = deleteNone(
                {
                    "microtenant_id": desired_group.get("microtenant_id"),
                    "name": desired_group.get("name"),
                    "description": desired_group.get("description"),
                    "enabled": desired_group.get("enabled"),
                }
            )
            created, _unused, error = client.segment_groups.add_group(**payload)
            if error:
                module.fail_json(
                    msg=f"Error creating segment group: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_group and existing_group.get("id"):
        _unused, _unused, error = client.segment_groups.delete_group(
            group_id=existing_group.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting segment group: {to_native(error)}")
        module.exit_json(changed=True, data=existing_group)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", default=True, required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
