#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_server_group
short_description: Create a Server Group .
description:
  - This module create/update/delete a Server Group resource in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
    - zscaler.zpacloud.fragments.enabled_state
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
    required: False
    description:
      - This field is the description of the server group.
  enabled:
    type: bool
    required: false
    description:
      - This field defines if the server group is enabled or disabled.
  dynamic_discovery:
    type: bool
    required: false
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

EXAMPLES = """
- name: Create/Update/Delete a Server Group - Dynamic Discovery Off
  zscaler.zpacloud.zpa_server_group:
    provider: "{{ zpa_cloud }}"
    name: "Example"
    description: "Example"
    enabled: false
    dynamic_discovery: false
    app_connector_group_ids:
      - id: "216196257331291921"
    server_ids:
      - id: "216196257331291921"
"""

RETURN = """
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

    desired_app = normalize_app(server_group)
    current_app = normalize_app(existing_server_group) if existing_server_group else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_app.items():
        if key not in fields_to_exclude and current_app.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_app.get(key)}, Desired: {value}"
            )

    if existing_server_group is not None:
        id = existing_server_group.get("id")
        existing_server_group.update(server_group)
        existing_server_group["id"] = id

    if state == "present":
        if existing_server_group is not None:
            if differences_detected:
                """Update"""
                existing_server_group = deleteNone(
                    {
                        "group_id": existing_server_group.get("id"),
                        "name": existing_server_group.get("name"),
                        "description": existing_server_group.get("description"),
                        "enabled": existing_server_group.get("enabled"),
                        "app_connector_group_ids": existing_server_group.get(
                            "app_connector_group_ids"
                        ),
                        "dynamic_discovery": existing_server_group.get(
                            "dynamic_discovery"
                        ),
                        "server_ids": existing_server_group.get("server_ids"),
                    }
                )
                existing_server_group = client.server_groups.update_group(
                    **existing_server_group
                )
                module.exit_json(changed=True, data=existing_server_group)
            else:
                # No Changes Needed
                module.exit_json(changed=False, data=existing_server_group)
        else:
            """Create"""
            server_group = deleteNone(
                {
                    "name": server_group.get("name"),
                    "app_connector_group_ids": server_group.get(
                        "app_connector_group_ids"
                    ),
                    "description": server_group.get("description"),
                    "enabled": server_group.get("enabled"),
                    "dynamic_discovery": server_group.get("dynamic_discovery"),
                    "server_ids": server_group.get("server_ids"),
                }
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
        enabled=dict(type="bool", required=False, default=True),
        description=dict(type="str", required=False),
        dynamic_discovery=dict(type="bool", required=False),
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
