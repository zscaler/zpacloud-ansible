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
module: zpa_user_portal_aup
short_description: Create a User Portal Acceptable Use Policy (AUP)
description:
    - This module will create/update/delete a User Portal Acceptable Use Policy (AUP) resource.
    - The AUP defines the terms and conditions that users must accept when accessing the portal.
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
    description: "The unique identifier of the User Portal AUP"
    type: str
    required: false
  name:
    description: "Name of the User Portal AUP"
    type: str
    required: false
  description:
    description: "Description of the User Portal AUP"
    type: str
    required: false
  enabled:
    description: "Whether this User Portal AUP is enabled or not"
    type: bool
    required: false
  aup:
    description: "The Acceptable Use Policy text content that users must accept"
    type: str
    required: false
  email:
    description: "Contact email address for the AUP"
    type: str
    required: false
  phone_num:
    description: "Contact phone number for the AUP"
    type: str
    required: false
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Create/Update/Delete a User Portal AUP
  zscaler.zpacloud.zpa_user_portal_aup:
    provider: "{{ zpa_cloud }}"
    name: Standard AUP
    description: Standard Acceptable Use Policy for all users
    enabled: true
    aup: "By accessing this portal, you agree to comply with all company policies..."
    email: "admin@example.com"
    phone_num: "+1-555-123-4567"
"""

RETURN = """
# The newly created User Portal AUP resource record.
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
    params = ["id", "name", "description", "enabled", "aup", "email", "phone_num", "microtenant_id"]
    aup_data = {param: module.params.get(param) for param in params}
    aup_id = aup_data.get("id")
    aup_name = aup_data.get("name")
    microtenant_id = aup_data.get("microtenant_id")

    # Step 1: Fetch existing AUP if possible
    existing_aup = None
    if aup_id:
        result, _unused, error = client.user_portal_aup.get_user_portal_aup(
            aup_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving User Portal AUP by ID {aup_id}: {to_native(error)}"
            )
        if result:
            existing_aup = result.as_dict()

    elif aup_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        aup_list, error = collect_all_items(
            client.user_portal_aup.list_user_portal_aup, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing User Portal AUPs: {to_native(error)}")
        for item in aup_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == aup_name:
                existing_aup = item_dict
                break

    # Step 2: Normalize and compare
    desired_aup = normalize_app(aup_data)
    current_aup = normalize_app(existing_aup) if existing_aup else {}

    fields_to_ignore = ["id"]

    drift = any(
        desired_aup.get(k) != current_aup.get(k)
        for k in desired_aup
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_aup))
            or (state == "absent" and existing_aup)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_aup:
            if drift:
                update_aup = deleteNone(
                    {
                        "microtenant_id": desired_aup.get("microtenant_id"),
                        "name": desired_aup.get("name"),
                        "description": desired_aup.get("description"),
                        "enabled": desired_aup.get("enabled"),
                        "aup": desired_aup.get("aup"),
                        "email": desired_aup.get("email"),
                        "phone_num": desired_aup.get("phone_num"),
                    }
                )
                updated, _unused, error = client.user_portal_aup.update_user_portal_aup(
                    portal_id=existing_aup.get("id"), **update_aup
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating User Portal AUP: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_aup)
        else:
            payload = deleteNone(
                {
                    "microtenant_id": desired_aup.get("microtenant_id"),
                    "name": desired_aup.get("name"),
                    "description": desired_aup.get("description"),
                    "enabled": desired_aup.get("enabled"),
                    "aup": desired_aup.get("aup"),
                    "email": desired_aup.get("email"),
                    "phone_num": desired_aup.get("phone_num"),
                }
            )
            created, _unused, error = client.user_portal_aup.add_user_portal_aup(**payload)
            if error:
                module.fail_json(
                    msg=f"Error creating User Portal AUP: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_aup and existing_aup.get("id"):
        _unused, _unused, error = client.user_portal_aup.delete_user_portal_aup(
            portal_id=existing_aup.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting User Portal AUP: {to_native(error)}")
        module.exit_json(changed=True, data=existing_aup)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        aup=dict(type="str", required=False),
        email=dict(type="str", required=False),
        phone_num=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
