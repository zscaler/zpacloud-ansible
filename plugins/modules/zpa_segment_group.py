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
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    group = dict()
    params = [
        "id",
        "name",
        "description",
        "enabled",
    ]
    for param_name in params:
        group[param_name] = module.params.get(param_name, None)
    group_id = group.get("id", None)
    group_name = group.get("name", None)

    existing_group = None
    if group_id is not None:
        group_box = client.segment_groups.get_group(group_id=group_id)
        if group_box is not None:
            existing_group = group_box.to_dict()
    elif group_name is not None:
        groups = client.segment_groups.list_groups().to_list()
        for group_ in groups:
            if group_.get("name") == group_name:
                existing_group = group_
                break

    desired_app = normalize_app(group)
    current_app = normalize_app(existing_group) if existing_group else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_app.items():
        if key not in fields_to_exclude and current_app.get(key) != value:
            differences_detected = True
            # module.warn(
            #     f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {value}"
            # )

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_group is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_group is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_group is not None:
        id = existing_group.get("id")
        existing_group.update(group)
        existing_group["id"] = id

    if state == "present":
        if existing_group is not None:
            if differences_detected:
                """Update"""
                existing_group = deleteNone(
                    {
                        "group_id": existing_group.get("id"),
                        "name": existing_group.get("name"),
                        "description": existing_group.get("description"),
                        "enabled": existing_group.get("enabled"),
                    }
                )
                existing_group = client.segment_groups.update_group(
                    **existing_group
                ).to_dict()
                module.exit_json(changed=True, data=existing_group)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_group)
        else:
            """Create"""
            group = deleteNone(
                {
                    "name": group.get("name"),
                    "description": group.get("description"),
                    "enabled": group.get("enabled"),
                }
            )
            group = client.segment_groups.add_group(**group).to_dict()
            module.exit_json(changed=True, data=group)
    elif (
        state == "absent"
        and existing_group is not None
        and existing_group.get("id") is not None
    ):
        code = client.segment_groups.delete_group(group_id=existing_group.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_group)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
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
