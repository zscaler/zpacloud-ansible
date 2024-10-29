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

    group_id = server_group.get("id", None)
    group_name = server_group.get("name", None)

    existing_server_group = None
    if group_id is not None:
        group_box = client.server_groups.get_group(group_id=group_id)
        if group_box is not None:
            existing_server_group = group_box.to_dict()
    elif group_name is not None:
        groups = client.server_groups.list_groups().to_list()
        for group_ in groups:
            if group_.get("name") == group_name:
                existing_server_group = group_
                break

    # Debugging: Display the current state (what Ansible sees from the API)
    # module.warn(f"Current server group from API: {existing_server_group}")

    desired_app = normalize_app(server_group)
    current_app = normalize_app(existing_server_group) if existing_server_group else {}

    # Debugging: Show normalized values for comparison
    # module.warn(f"Normalized Desired: {desired_app}")
    # module.warn(f"Normalized Current: {current_app}")

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_app.items():
        # Debugging: Track comparisons for each key-value pair
        # module.warn(f"Comparing key: {key}, Desired: {value}, Current: {current_app.get(key)}")

        if key not in fields_to_exclude and current_app.get(key) != value:
            differences_detected = True
            # module.warn(f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {value}")

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (
            existing_server_group is None or differences_detected
        ):
            module.exit_json(changed=True)
        elif state == "absent" and existing_server_group is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_server_group is not None:
        id = existing_server_group.get("id")
        existing_server_group.update(server_group)
        existing_server_group["id"] = id

    # module.warn(f"Final payload being sent to SDK: {server_group}")
    if state == "present":
        if existing_server_group is not None:
            if differences_detected:
                """Update"""
                existing_server_group = deleteNone(
                    dict(
                        group_id=existing_server_group.get("id"),
                        name=existing_server_group.get("name", None),
                        description=existing_server_group.get("description", None),
                        enabled=existing_server_group.get("enabled", None),
                        app_connector_group_ids=existing_server_group.get(
                            "app_connector_group_ids", None
                        ),
                        dynamic_discovery=existing_server_group.get(
                            "dynamic_discovery", None
                        ),
                        server_ids=existing_server_group.get("server_ids", None),
                    )
                )
                # module.warn(f"Payload Update for SDK: {existing_server_group}")
                existing_server_group = client.server_groups.update_group(
                    **existing_server_group
                )
                module.exit_json(changed=True, data=existing_server_group)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_server_group)
        else:
            """Create"""
            server_group = deleteNone(
                dict(
                    name=server_group.get("name", None),
                    app_connector_group_ids=server_group.get(
                        "app_connector_group_ids", None
                    ),
                    description=server_group.get("description", None),
                    enabled=server_group.get("enabled", None),
                    dynamic_discovery=server_group.get("dynamic_discovery", None),
                    server_ids=server_group.get("server_ids", None),
                )
            )
            server_group = client.server_groups.add_group(**server_group).to_dict()
            module.exit_json(changed=True, data=server_group)
    elif state == "absent" and existing_server_group is not None:
        code = client.server_groups.delete_group(existing_server_group.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_server_group)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str"),
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
