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

DOCUMENTATION = r"""
---
module: zpa_server_group
short_description: Create a Server Group
description:
  - This module create/update/delete a Server Group resource in the ZPA Cloud.
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
    type: str
    description: ""
    required: False
  name:
    type: str
    required: True
    description:
      - This field defines the name of the server group.
  description:
    type: str
    required: false
    description:
      - This field is the description of the server group.
  enabled:
    type: bool
    required: false
    default: true
    description:
      - This field defines if the server group is enabled or disabled.
  dynamic_discovery:
    type: bool
    required: false
    default: true
    description:
      - This field controls dynamic discovery of the servers.
  server_ids:
    type: list
    elements: str
    required: false
    description:
      - This field is a list of servers objects that are applicable only when dynamic discovery is disabled.
      - Server name is required only in cases where the new servers need to be created in this API. For existing servers, pass only the serverId.
  app_connector_group_ids:
    type: list
    elements: str
    required: false
    description:
      - List of server_group-connector ID objects.
"""

EXAMPLES = r"""
- name: Create/Update/Delete a Server Group - Dynamic Discovery On
  zscaler.zpacloud.zpa_server_group:
    provider: "{{ zpa_cloud }}"
    name: "Example"
    description: "Example"
    enabled: true
    dynamic_discovery: true
    app_connector_group_ids:
      - id: "216196257331291921"

- name: Create/Update/Delete a Server Group - Dynamic Discovery Off
  zscaler.zpacloud.zpa_server_group:
    provider: "{{ zpa_cloud }}"
    name: "Example"
    description: "Example"
    enabled: true
    dynamic_discovery: false
    app_connector_group_ids:
      - id: "216196257331291921"
    server_ids:
      - id: "216196257331291921"
"""

RETURN = r"""
# The newly created server group resource record.
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
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    server_group = dict()
    params = [
        "id",
        "microtenant_id",
        "name",
        "description",
        "enabled",
        "dynamic_discovery",
        "server_ids",
        "app_connector_group_ids",
    ]
    for param_name in params:
        server_group[param_name] = module.params.get(param_name, None)

    # Debugging: Display the desired state
    # module.warn(f"Desired server group: {server_group}")

    group_id = server_group.get("id")
    group_name = server_group.get("name")
    microtenant_id = server_group.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_group = None
    if group_id is not None:
        result, _, error = client.server_groups.get_group(
            group_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching server group with id {group_id}: {to_native(error)}"
            )
        existing_group = result.as_dict()
    else:
        result, error = collect_all_items(
            client.server_groups.list_groups, query_params
        )
        if error:
            module.fail_json(msg=f"Error server groups: {to_native(error)}")
        if result:
            for group_ in result:
                if group_.name == group_name:
                    existing_group = group_.as_dict()
                    break

    # Debugging: Display the current state (what Ansible sees from the API)
    module.warn(f"Current server group from API: {existing_group}")

    desired_group = normalize_app(server_group)
    current_group = normalize_app(existing_group) if existing_group else {}

    # Debugging: Show normalized values for comparison
    module.warn(f"Normalized Desired: {desired_group}")
    module.warn(f"Normalized Current: {current_group}")

    # 🔧 Normalize current_group: convert app_connector_groups to app_connector_group_ids
    if "app_connector_groups" in current_group:
        current_group["app_connector_group_ids"] = sorted(
            [
                g.get("id")
                for g in current_group.get("app_connector_groups", [])
                if g.get("id")
            ]
        )
        del current_group["app_connector_groups"]

    # 🔧 Normalize desired_group: ensure app_connector_group_ids is sorted for accurate comparison
    if (
        "app_connector_group_ids" in desired_group
        and desired_group["app_connector_group_ids"]
    ):
        desired_group["app_connector_group_ids"] = sorted(
            desired_group["app_connector_group_ids"]
        )

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_group.items():
        # Debugging: Track comparisons for each key-value pair
        module.warn(
            f"Comparing key: {key}, Desired: {value}, Current: {current_group.get(key)}"
        )

        if key not in fields_to_exclude and current_group.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_group.get(key)}, Desired: {value}"
            )

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
        existing_group.update(server_group)
        existing_group["id"] = id

    module.warn(f"Final payload being sent to SDK: {server_group}")
    if state == "present":
        if existing_group is not None:
            if differences_detected:
                """Update"""
                update_group = deleteNone(
                    {
                        "group_id": existing_group.get("id"),
                        "microtenant_id": desired_group.get("microtenant_id", None),
                        "name": desired_group.get("name", None),
                        "description": desired_group.get("description", None),
                        "enabled": desired_group.get("enabled", None),
                        "app_connector_group_ids": desired_group.get(
                            "app_connector_group_ids", None
                        ),
                        "dynamic_discovery": desired_group.get(
                            "dynamic_discovery", None
                        ),
                        "server_ids": desired_group.get("server_ids", None),
                    }
                )
                module.warn(f"Payload Update for SDK: {update_group}")
                updated_group, _, error = client.server_groups.update_group(
                    group_id=update_group.pop("group_id"), **update_group
                )
                if error:
                    module.fail_json(msg=f"Error updating group: {to_native(error)}")
                module.exit_json(changed=True, data=updated_group.as_dict())
            else:
                module.exit_json(changed=False, data=existing_group)
        else:
            """Create"""
            create_group = deleteNone(
                {
                    "microtenant_id": desired_group.get("microtenant_id", None),
                    "name": desired_group.get("name", None),
                    "description": desired_group.get("description", None),
                    "enabled": desired_group.get("enabled", None),
                    "dynamic_discovery": desired_group.get("dynamic_discovery", None),
                    "app_connector_group_ids": desired_group.get(
                        "app_connector_group_ids", None
                    ),
                    "server_ids": desired_group.get("server_ids", None),
                }
            )
            module.warn("Payload Update for SDK: {}".format(create_group))
            created, _, error = client.server_groups.add_group(**create_group)
            if error:
                module.fail_json(msg=f"Error creating group: {to_native(error)}")
            module.exit_json(changed=True, data=created.as_dict())

    elif state == "absent":
        if existing_group:
            _, _, error = client.server_groups.delete_group(
                group_id=existing_group.get("id"),
                microtenant_id=microtenant_id,
            )
        if error:
            module.fail_json(msg=f"Error deleting group: {to_native(error)}")
        module.exit_json(changed=True, data=existing_group)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str"),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        enabled=dict(type="bool", default=True, required=False),
        description=dict(type="str", required=False),
        dynamic_discovery=dict(type="bool", default=True, required=False),
        server_ids=dict(type="list", elements="str", required=False),
        app_connector_group_ids=dict(type="list", elements="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
