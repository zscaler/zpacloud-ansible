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
module: zpa_application_server
short_description: Create an application server in the ZPA Cloud.
description:
    - This module creates/update/delete an application server in the ZPA Cloud.
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

options:
    id:
        description: "The unique identifier of the server."
        required: false
        type: str
    name:
        description:
            - This field defines the name of the server.
        required: true
        type: str
    description:
        description:
            - This field defines the description of the server.
        required: false
        type: str
    enabled:
        description:
            - This field defines the status of the server, true or false.
        required: false
        type: bool
        default: true
    address:
        description: "This field defines the domain or IP address of the server"
        required: false
        type: str
    app_server_group_ids:
        description:
            - This field defines the list of server groups IDs
        required: false
        type: list
        elements: str
    state:
        description:
            - The state of the module, which determines if the settings are to be applied.
        type: str
        choices: ['absent', 'present', gathered]
        default: 'present'
"""

EXAMPLES = """
- name: Create Second Application Server
  zscaler.zpacloud.zpa_application_server:
    provider: "{{ zpa_cloud }}"
    name: Example1
    description: Example1
    address: example.acme.com
    enabled: true
    app_server_group_ids: []
"""

RETURN = """
# The newly created application server resource record.
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
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect input parameters
    params = [
        "id",
        "name",
        "description",
        "address",
        "enabled",
        "app_server_group_ids",
        "microtenant_id",
    ]
    server = {param: module.params.get(param) for param in params}
    server_id = server.get("id")
    server_name = server.get("name")
    microtenant_id = server.get("microtenant_id")

    existing_server = None

    # Fetch by ID
    if server_id:
        result, _, error = client.servers.get_server(
            server_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(msg=f"Error retrieving server by ID: {to_native(error)}")
        if result:
            existing_server = result.as_dict()

    # Fetch by Name
    elif server_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        server_list, _, error = client.servers.list_servers(query_params)
        if error:
            module.fail_json(msg=f"Error listing servers: {to_native(error)}")
        for item in server_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == server_name:
                existing_server = item_dict
                break

    # Drift detection logic
    desired = normalize_app(server)
    current = normalize_app(existing_server) if existing_server else {}

    drift_keys = []
    for k in desired:
        if k == "id":
            continue

        desired_val = desired.get(k)
        current_val = current.get(k)

        # Handle [] vs None comparison for app_server_group_ids
        if k == "app_server_group_ids":
            if not desired_val and not current_val:
                continue  # No drift if both are empty or None

        if desired_val != current_val:
            drift_keys.append(k)
            module.warn(f"[DRIFT] {k}: current={current_val} | desired={desired_val}")

    drift = bool(drift_keys)
    module.warn(f"[DRIFT] Detected: {drift} | Keys: {drift_keys or 'None'}")

    if module.check_mode:
        if state == "present" and (not existing_server or drift):
            module.exit_json(changed=True)
        elif state == "absent" and existing_server:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if state == "present":
        if existing_server:
            if drift:
                payload = deleteNone(
                    {
                        "server_id": existing_server.get("id"),
                        "name": desired.get("name"),
                        "description": desired.get("description"),
                        "address": desired.get("address"),
                        "enabled": desired.get("enabled"),
                        "app_server_group_ids": desired.get("app_server_group_ids"),
                        "microtenant_id": desired.get("microtenant_id"),
                    }
                )
                updated, _, error = client.servers.update_server(**payload)
                if error:
                    module.fail_json(msg=f"Error updating server: {to_native(error)}")
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_server)
        else:
            payload = deleteNone(
                {
                    "name": desired.get("name"),
                    "description": desired.get("description"),
                    "address": desired.get("address"),
                    "enabled": desired.get("enabled"),
                    "app_server_group_ids": desired.get("app_server_group_ids"),
                    "microtenant_id": desired.get("microtenant_id"),
                }
            )
            created, _, error = client.servers.add_server(**payload)
            if error:
                module.fail_json(msg=f"Error creating server: {to_native(error)}")
            module.exit_json(changed=True, data=created.as_dict())

    elif state == "absent" and existing_server:
        _, _, error = client.servers.delete_server(
            server_id=existing_server.get("id"), microtenant_id=microtenant_id
        )
        if error:
            module.fail_json(msg=f"Error deleting server: {to_native(error)}")
        module.exit_json(changed=True, data=existing_server)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        address=dict(type="str", required=False),
        enabled=dict(type="bool", default=True, required=False),
        app_server_group_ids=dict(type="list", elements="str", required=False),
        state=dict(
            type="str", choices=["present", "absent", "gathered"], default="present"
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
