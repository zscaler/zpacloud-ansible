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
notes:
    - Check mode is supported.
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
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Gather Details of a Specific Browser Certificates by Name
  zscaler.zpacloud.zpa_ba_certificate_info:
    provider: "{{ zpa_cloud }}"
    name: 'portal.acme.com'
    register: cert_name

- name: Get details of a specific SECURE_REMOTE_ACCESS application segment by name
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: SECURE_REMOTE_ACCESS
    name: pra_app_segment01
    register: pra_app_segment01

- name: Create/Update/Delete PRA Console
  zscaler.zpacloud.zpa_pra_portal_controller:
    provider: "{{ zpa_cloud }}"
    name: 'portal.acme.com'
    description: 'PRA Console'
    enabled: true
    domain: 'portal.acme.com'
    certificate_id: "{{ cert_name.certificates[0].id }}"
    user_notification: 'PRA Console'
    user_notification_enabled: true
    register: portal

- name: Create PRA Console
  zscaler.zpacloud.zpa_pra_console_controller:
    provider: "{{ zpa_cloud }}"
    name: 'PRA Console'
    description: 'PRA Console'
    enabled: true
    pra_application_id: "{{ pra_app_segment01.apps[0].id }}"
    pra_portal_ids:
      - "{{ portal.data.id }}"
    register: result
"""

RETURN = """
# The newly created privileged console resource record.
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_console(console):
    """
    Normalize PRA Console data by setting computed values.
    """
    normalized = console.copy()

    computed_values = []
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    console = dict()
    params = [
        "id",
        "microtenant_id",
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
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_console = None
    if console_id is not None:
        result, _unused, error = client.pra_console.get_console(
            console_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching pra console with id {console_id}: {to_native(error)}"
            )
        existing_console = result.as_dict()
    else:
        result, error = collect_all_items(
            client.pra_console.list_consoles, query_params
        )
        if error:
            module.fail_json(msg=f"Error pra consoles: {to_native(error)}")
        if result:
            for console_ in result:
                if console_.name == console_name:
                    existing_console = console_.as_dict()
                    break

    desired_console = normalize_console(console)
    current_console = normalize_console(existing_console) if existing_console else {}

    # 🔧 Normalize current_group: convert app_connector_groups to pra_portal_ids
    if "pra_portals" in current_console:
        current_console["pra_portal_ids"] = sorted(
            [g.get("id") for g in current_console.get("pra_portals", []) if g.get("id")]
        )
        del current_console["pra_portals"]

    # 🔧 Normalize desired_group: ensure pra_portal_ids is sorted for accurate comparison
    if "pra_portal_ids" in desired_console and desired_console["pra_portal_ids"]:
        desired_console["pra_portal_ids"] = sorted(desired_console["pra_portal_ids"])

    if "pra_application" in current_console:
        current_console["pra_application_id"] = current_console["pra_application"].get(
            "id"
        )
        del current_console["pra_application"]

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_console.items():
        if key not in fields_to_exclude and current_console.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_console.get(key)}, Desired: {value}"
            )

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_console is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_console is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_console is not None:
        id = existing_console.get("id")
        existing_console.update(console)
        existing_console["id"] = id

    module.warn(f"Final payload being sent to SDK: {console}")
    if state == "present":
        if existing_console is not None:
            if differences_detected:
                """Update"""
                update_console = deleteNone(
                    {
                        "console_id": existing_console.get("id"),
                        "microtenant_id": desired_console.get("microtenant_id", None),
                        "name": desired_console.get("name"),
                        "description": desired_console.get("description"),
                        "enabled": desired_console.get("enabled"),
                        "icon_text": desired_console.get("icon_text"),
                        "pra_application_id": desired_console.get("pra_application_id"),
                        "pra_portal_ids": list(
                            desired_console.get("pra_portal_ids", [])
                        ),
                    }
                )
                module.warn("Payload Update for SDK: {}".format(update_console))
                updated_console, _unused, error = client.pra_console.update_console(
                    console_id=update_console.pop("console_id"), **existing_console
                )
                if error:
                    module.fail_json(msg=f"Error updating console: {to_native(error)}")
                module.exit_json(changed=True, data=updated_console.as_dict())
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_console)
        else:
            module.warn("Creating pra console as no existing console was found")
            """Create"""
            create_console = deleteNone(
                {
                    "microtenant_id": desired_console.get("microtenant_id", None),
                    "name": desired_console.get("name"),
                    "description": desired_console.get("description"),
                    "enabled": desired_console.get("enabled"),
                    "icon_text": desired_console.get("icon_text"),
                    "pra_application_id": desired_console.get("pra_application_id"),
                    "pra_portal_ids": list(desired_console.get("pra_portal_ids", [])),
                }
            )
            module.warn(f"Payload for SDK: {create_console}")
            new_console, _unused, error = client.pra_console.add_console(
                **create_console
            )
            if error:
                module.fail_json(msg=f"Error creating console: {to_native(error)}")
            module.exit_json(changed=True, data=new_console.as_dict())

    elif state == "absent":
        if existing_console:
            _unused, _unused, error = client.pra_console.delete_console(
                console_id=existing_console.get("id"),
                microtenant_id=microtenant_id,
            )
        if error:
            module.fail_json(msg=f"Error deleting console: {to_native(error)}")
        module.exit_json(changed=True, data=existing_console)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
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
