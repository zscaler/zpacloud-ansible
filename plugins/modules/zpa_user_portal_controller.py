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
module: zpa_user_portal_controller
short_description: Create a User Portal Controller
description:
    - This module will create/update/delete a User Portal Controller resource.
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
    description: "The unique identifier of the User Portal Controller"
    type: str
    required: false
  name:
    description: "Name of the User Portal Controller"
    type: str
    required: true
  description:
    description: "Description of the User Portal Controller"
    type: str
    required: false
  enabled:
    description: "Whether this User Portal Controller is enabled or not"
    type: bool
    required: false
  certificate_id:
    description: "Certificate ID for the User Portal Controller"
    type: str
    required: false
  domain:
    description: "Domain for the User Portal Controller"
    type: str
    required: false
  ext_domain:
    description: "External domain for the User Portal Controller"
    type: str
    required: false
  ext_domain_name:
    description: "External domain name for the User Portal Controller"
    type: str
    required: false
  ext_domain_translation:
    description: "External domain translation for the User Portal Controller"
    type: str
    required: false
  ext_label:
    description: "External label for the User Portal Controller"
    type: str
    required: false
  user_notification:
    description: "User notification message for the User Portal Controller"
    type: str
    required: false
  user_notification_enabled:
    description: "Whether user notifications are enabled for the User Portal Controller"
    type: bool
    required: false
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Create/Update/Delete a User Portal Controller
  zscaler.zpacloud.zpa_user_portal_controller:
    provider: "{{ zpa_cloud }}"
    name: UserPortal01
    description: User Portal for corporate access
    enabled: true
    user_notification: "Welcome to the corporate portal"
    user_notification_enabled: true
    ext_label: "portal01"
    ext_domain: "portal.example.com"
    ext_domain_name: "ext-portal-example.zscalerportal.net"
"""

RETURN = """
# The newly created User Portal Controller resource record.
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
        "certificate_id",
        "domain",
        "ext_domain",
        "ext_domain_name",
        "ext_domain_translation",
        "ext_label",
        "user_notification",
        "user_notification_enabled",
        "microtenant_id",
    ]
    portal_data = {param: module.params.get(param) for param in params}
    portal_id = portal_data.get("id")
    portal_name = portal_data.get("name")
    microtenant_id = portal_data.get("microtenant_id")

    # Step 1: Fetch existing portal if possible
    existing_portal = None
    if portal_id:
        result, _unused, error = client.user_portal_controller.get_user_portal(
            portal_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving User Portal Controller by ID {portal_id}: {to_native(error)}"
            )
        if result:
            existing_portal = result.as_dict()

    elif portal_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        portal_list, error = collect_all_items(
            client.user_portal_controller.list_user_portals, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing User Portal Controllers: {to_native(error)}")
        for item in portal_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == portal_name:
                existing_portal = item_dict
                break

    # Step 2: Normalize and compare
    desired_portal = normalize_app(portal_data)
    current_portal = normalize_app(existing_portal) if existing_portal else {}

    fields_to_ignore = ["id"]

    drift = any(
        desired_portal.get(k) != current_portal.get(k)
        for k in desired_portal
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_portal))
            or (state == "absent" and existing_portal)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_portal:
            if drift:
                update_portal = deleteNone(
                    {
                        "microtenant_id": desired_portal.get("microtenant_id"),
                        "name": desired_portal.get("name"),
                        "description": desired_portal.get("description"),
                        "enabled": desired_portal.get("enabled"),
                        "certificate_id": desired_portal.get("certificate_id"),
                        "domain": desired_portal.get("domain"),
                        "ext_domain": desired_portal.get("ext_domain"),
                        "ext_domain_name": desired_portal.get("ext_domain_name"),
                        "ext_domain_translation": desired_portal.get("ext_domain_translation"),
                        "ext_label": desired_portal.get("ext_label"),
                        "user_notification": desired_portal.get("user_notification"),
                        "user_notification_enabled": desired_portal.get("user_notification_enabled"),
                    }
                )
                updated, _unused, error = client.user_portal_controller.update_user_portal(
                    portal_id=existing_portal.get("id"), **update_portal
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating User Portal Controller: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_portal)
        else:
            payload = deleteNone(
                {
                    "microtenant_id": desired_portal.get("microtenant_id"),
                    "name": desired_portal.get("name"),
                    "description": desired_portal.get("description"),
                    "enabled": desired_portal.get("enabled"),
                    "certificate_id": desired_portal.get("certificate_id"),
                    "domain": desired_portal.get("domain"),
                    "ext_domain": desired_portal.get("ext_domain"),
                    "ext_domain_name": desired_portal.get("ext_domain_name"),
                    "ext_domain_translation": desired_portal.get("ext_domain_translation"),
                    "ext_label": desired_portal.get("ext_label"),
                    "user_notification": desired_portal.get("user_notification"),
                    "user_notification_enabled": desired_portal.get("user_notification_enabled"),
                }
            )
            created, _unused, error = client.user_portal_controller.add_user_portal(**payload)
            if error:
                module.fail_json(
                    msg=f"Error creating User Portal Controller: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_portal and existing_portal.get("id"):
        _unused, _unused, error = client.user_portal_controller.delete_user_portal(
            portal_id=existing_portal.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting User Portal Controller: {to_native(error)}")
        module.exit_json(changed=True, data=existing_portal)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        certificate_id=dict(type="str", required=False),
        domain=dict(type="str", required=False),
        ext_domain=dict(type="str", required=False),
        ext_domain_name=dict(type="str", required=False),
        ext_domain_translation=dict(type="str", required=False),
        ext_label=dict(type="str", required=False),
        user_notification=dict(type="str", required=False),
        user_notification_enabled=dict(type="bool", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()

