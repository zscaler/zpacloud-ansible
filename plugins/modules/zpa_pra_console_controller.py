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
module: zpa_pra_console_controller
short_description: Create a PRA Console Controller.
description:
  - This module will create/update/delete Privileged Remote Access Console.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  id:
    type: str
    description: "The unique identifier of the privileged console"
    required: false
  name:
    type: str
    description: "The name of the privileged console"
    required: true
  description:
    type: str
    description: "The description of the privileged console"
    required: false
  enabled:
    type: bool
    description:
        - Whether or not the privileged console is enabled
    required: false
    default: true
  icon_text:
    type: str
    description:
        - The privileged console icon. The icon image is converted to base64 encoded text format
    required: false
  pra_portal_ids:
    description:
      - The unique identifier of the privileged portal.
    type: list
    elements: str
    required: false
  pra_application_id:
    description:
      - The unique identifier of the Privileged Remote Access-enabled application.
    type: str
    required: false
"""

EXAMPLES = """
- name: Gather Details of a Specific Browser Certificates by Name
  zscaler.zpacloud.zpa_ba_certificate_facts:
    provider: '{{ zpa_cloud }}'
    name: 'portal.acme.com'
  register: cert_name

- name: Create/Update/Delete PRA Portal
  zscaler.zpacloud.zpa_pra_portal_controller:
    provider: '{{ zpa_cloud }}'
    name: 'portal.acme.com'
    description: 'Created with Ansible'
    enabled: true
    domain: 'portal.acme.com'
    certificate_id: "{{ cert_name.data[0].id }}"
    user_notification: 'Created with Ansible'
    user_notification_enabled: true
  register: result
"""

RETURN = """
# The newly created privileged portal resource record.
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_console(console):
    """
    Normalize pra portal data by setting computed values.
    """
    normalized = console.copy()

    computed_values = [
        "pra_application_id",
        "pra_portal_ids",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    console = dict()
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "icon_text",
        "pra_application_id",
        "pra_portal_ids",
    ]
    for param_name in params:
        console[param_name] = module.params.get(param_name, None)
    console_id = console.get("id", None)
    console_name = console.get("name", None)

    existing_console = None
    if console_id is not None:
        console_box = client.privileged_remote_access.get_console(console_id=console_id)
        if console_box is not None:
            existing_console = console_box.to_dict()
    elif console_name is not None:
        consoles = client.privileged_remote_access.list_consoles().to_list()
        for console_ in consoles:
            if console_.get("name") == console_name:
                existing_console = console_
                break

    desired_console = normalize_console(console)
    current_console = normalize_console(existing_console) if existing_console else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_console.items():
        if key not in fields_to_exclude and current_console.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_console.get(key)}, Desired: {value}"
            )

    if existing_console is not None:
        id = existing_console.get("id")
        existing_console.update(console)
        existing_console["id"] = id

    module.warn(f"Final payload being sent to SDK: {console}")
    if state == "present":
        if existing_console is not None:
            if differences_detected:
                """Update"""
                update_payload = {
                    "console_id": existing_console.get("id"),
                    "name": existing_console.get("name"),
                    "description": existing_console.get("description"),
                    "enabled": existing_console.get("enabled"),
                    "icon_text": existing_console.get("icon_text"),
                    "pra_application_id": console.get("pra_application_id"),
                    "pra_portal_ids": list(console.get("pra_portal_ids", [])),
                }
                existing_console = client.privileged_remote_access.update_console(
                    **deleteNone(update_payload)
                ).to_dict()
                module.exit_json(changed=True, data=existing_console)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_console)
        else:
            module.warn("Creating pra console as no existing console was found")
            """Create"""
            create_payload = {
                "name": console.get("name"),
                "description": console.get("description"),
                "enabled": console.get("enabled"),
                "icon_text": console.get("icon_text"),
                "pra_application_id": console.get("pra_application_id"),
                "pra_portal_ids": list(console.get("pra_portal_ids", [])),
            }
            module.warn(f"Payload for SDK: {create_payload}")
            portal_response = client.privileged_remote_access.add_console(
                **deleteNone(create_payload)
            )
            module.exit_json(changed=True, data=portal_response)
    elif (
        state == "absent"
        and existing_console is not None
        and existing_console.get("id") is not None
    ):
        code = client.privileged_remote_access.delete_console(
            portal_id=existing_console.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_console)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False, default=True),
        icon_text=dict(type="str", required=False),
        pra_portal_ids=dict(type="list", elements="str", required=False),
        pra_application_id=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
