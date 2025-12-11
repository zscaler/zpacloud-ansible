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
module: zpa_user_portal_link
short_description: Create a User Portal Link
description:
    - This module will create/update/delete a User Portal Link resource.
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
    description: "The unique identifier of the User Portal Link"
    type: str
    required: false
  name:
    description: "Name of the User Portal Link"
    type: str
    required: true
  description:
    description: "Description of the User Portal Link"
    type: str
    required: false
  enabled:
    description: "Whether this User Portal Link is enabled or not"
    type: bool
    required: false
  icon_text:
    description: "Icon text for the User Portal Link"
    type: str
    required: false
  link:
    description: "Link URL for the User Portal Link"
    type: str
    required: false
  link_path:
    description: "Link path for the User Portal Link"
    type: str
    required: false
  protocol:
    description: "Protocol for the User Portal Link (e.g., https://)"
    type: str
    required: false
  user_portal_link_ids:
    description: "List of User Portal IDs to associate with this link"
    type: list
    elements: str
    required: false
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Create/Update/Delete a User Portal Link
  zscaler.zpacloud.zpa_user_portal_link:
    provider: "{{ zpa_cloud }}"
    name: server1.example.com
    description: Portal link for accessing server1
    enabled: true
    link: "server1.example.com"
    protocol: "https://"
    icon_text: ""
    link_path: ""
    user_portal_link_ids:
      - "72058304855142822"
"""

RETURN = """
# The newly created User Portal Link resource record.
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
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "icon_text",
        "link",
        "link_path",
        "protocol",
        "user_portal_link_ids",
        "microtenant_id",
    ]
    link_data = {param: module.params.get(param) for param in params}
    link_id = link_data.get("id")
    link_name = link_data.get("name")
    microtenant_id = link_data.get("microtenant_id")

    # Step 1: Fetch existing link if possible
    existing_link = None
    if link_id:
        result, _unused, error = client.user_portal_link.get_portal_link(
            link_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving User Portal Link by ID {link_id}: {to_native(error)}"
            )
        if result:
            existing_link = result.as_dict()

    elif link_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        link_list, error = collect_all_items(
            client.user_portal_link.list_portal_link, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing User Portal Links: {to_native(error)}")
        for item in link_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == link_name:
                existing_link = item_dict
                break

    # Step 2: Normalize and compare
    desired_link = normalize_app(link_data)
    current_link = normalize_app(existing_link) if existing_link else {}

    # Convert user_portals (list of objects) to user_portal_link_ids (list of strings) for comparison
    current_portal_ids = []
    if current_link.get("user_portals"):
        current_portal_ids = sorted(
            [str(p.get("id")) for p in current_link.get("user_portals", []) if p.get("id")]
        )

    # Sort desired user_portal_link_ids for consistent comparison
    desired_portal_ids = []
    if desired_link.get("user_portal_link_ids"):
        desired_portal_ids = sorted(
            [str(pid) for pid in desired_link.get("user_portal_link_ids", [])]
        )

    # Fields to ignore in drift detection
    fields_to_ignore = ["id", "user_portals", "user_portal_link_ids", "microtenant_id"]

    # Helper function to normalize empty values for comparison
    def normalize_value(val):
        if val is None or val == "" or val == []:
            return None
        return val

    # Check drift for regular fields
    drift = False
    for k in desired_link:
        if k in fields_to_ignore:
            continue
        desired_val = normalize_value(desired_link.get(k))
        current_val = normalize_value(current_link.get(k))
        if desired_val is not None and desired_val != current_val:
            drift = True
            break

    # Check drift for user_portal_link_ids separately
    if not drift and desired_portal_ids != current_portal_ids:
        drift = True

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_link))
            or (state == "absent" and existing_link)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_link:
            if drift:
                update_link = deleteNone(
                    {
                        "microtenant_id": desired_link.get("microtenant_id"),
                        "name": desired_link.get("name"),
                        "description": desired_link.get("description"),
                        "enabled": desired_link.get("enabled"),
                        "icon_text": desired_link.get("icon_text"),
                        "link": desired_link.get("link"),
                        "link_path": desired_link.get("link_path"),
                        "protocol": desired_link.get("protocol"),
                        "user_portal_link_ids": desired_link.get("user_portal_link_ids"),
                    }
                )
                updated, _unused, error = client.user_portal_link.update_portal_link(
                    portal_link_id=existing_link.get("id"), **update_link
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating User Portal Link: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_link)
        else:
            payload = deleteNone(
                {
                    "microtenant_id": desired_link.get("microtenant_id"),
                    "name": desired_link.get("name"),
                    "description": desired_link.get("description"),
                    "enabled": desired_link.get("enabled"),
                    "icon_text": desired_link.get("icon_text"),
                    "link": desired_link.get("link"),
                    "link_path": desired_link.get("link_path"),
                    "protocol": desired_link.get("protocol"),
                    "user_portal_link_ids": desired_link.get("user_portal_link_ids"),
                }
            )
            created, _unused, error = client.user_portal_link.add_portal_link(**payload)
            if error:
                module.fail_json(
                    msg=f"Error creating User Portal Link: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_link and existing_link.get("id"):
        _unused, _unused, error = client.user_portal_link.delete_portal_link(
            portal_link_id=existing_link.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting User Portal Link: {to_native(error)}")
        module.exit_json(changed=True, data=existing_link)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        icon_text=dict(type="str", required=False),
        link=dict(type="str", required=False),
        link_path=dict(type="str", required=False),
        protocol=dict(type="str", required=False),
        user_portal_link_ids=dict(type="list", elements="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
