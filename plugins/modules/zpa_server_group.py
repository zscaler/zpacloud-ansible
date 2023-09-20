#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
options:
  client_id:
    description: ""
    required: false
    type: str
  client_secret:
    description: ""
    required: false
    type: str
  customer_id:
    description: ""
    required: false
    type: str
  applications:
    type: list
    elements: dict
    suboptions:
      name:
        required: false
        type: str
        description: ""
      id:
        required: true
        type: str
        description: ""
    required: false
    description:
      - This field is a json array of server_group-connector-id objects only.
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
  name:
    type: str
    required: True
    description:
      - This field defines the name of the server group.
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
  config_space:
    description:
      - config space.
    type: str
    required: false
    choices:
      - DEFAULT
      - SIEM
    default: DEFAULT
  description:
    type: str
    required: False
    description:
      - This field is the description of the server group.
  id:
    type: str
    description: ""
  ip_anchored:
    type: bool
    required: False
    description: ""
  state:
    description:
      - Whether the server group should be present or absent.
    default: present
    choices:
      - present
      - absent
    type: str

"""

EXAMPLES = """
- name: Create/Update/Delete a Server Group - Dynamic Discovery Off
  zscaler.zpacloud.zpa_server_group:
    name: "Example"
    description: "Example"
    enabled: false
    dynamic_discovery: false
    app_connector_group_ids:
      - id: "216196257331291921"
    server_ids:
      - id: "216196257331291921"
    application_ids:
      - id: "216196257331291921"
"""

RETURN = """
# The newly created server group resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
    deleteNone,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    server_group = dict()
    params = [
        "id",
        "ip_anchored",
        "name",
        "config_space",
        "enabled",
        "description",
        "dynamic_discovery",
        "server_ids",
        "application_ids",
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
    if existing_server_group is not None:
        id = existing_server_group.get("id")
        existing_server_group.update(server_group)
        existing_server_group["id"] = id
    if state == "present":
        if existing_server_group is not None:
            """Update"""
            existing_server_group = deleteNone(
                dict(
                    group_id=existing_server_group.get("id"),
                    app_connector_group_ids=existing_server_group.get(
                        "app_connector_group_ids"
                    ),
                    application_ids=existing_server_group.get("application_ids"),
                    config_space=existing_server_group.get("config_space"),
                    description=existing_server_group.get("description"),
                    enabled=existing_server_group.get("enabled"),
                    ip_anchored=existing_server_group.get("ip_anchored"),
                    dynamic_discovery=existing_server_group.get("dynamic_discovery"),
                    server_ids=existing_server_group.get("server_ids"),
                )
            )
            server_group = client.server_groups.update_group(**existing_server_group)
            module.exit_json(changed=True, data=server_group)
        else:
            """Create"""
            server_group = deleteNone(
                dict(
                    name=server_group.get("name"),
                    app_connector_group_ids=server_group.get("app_connector_group_ids"),
                    application_ids=server_group.get("application_ids"),
                    config_space=server_group.get("config_space"),
                    description=server_group.get("description"),
                    enabled=server_group.get("enabled"),
                    ip_anchored=server_group.get("ip_anchored"),
                    dynamic_discovery=server_group.get("dynamic_discovery"),
                    server_ids=server_group.get("server_ids"),
                )
            )
            server_group = client.server_groups.add_group(**server_group).to_dict()
            module.exit_json(changed=False, data=server_group)
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
        ip_anchored=dict(type="bool", required=False),
        name=dict(type="str", required=True),
        config_space=dict(
            type="str", required=False, default="DEFAULT", choices=["DEFAULT", "SIEM"]
        ),
        enabled=dict(type="bool", required=False),
        description=dict(type="str", required=False),
        dynamic_discovery=dict(type="bool", required=False),
        server_ids=dict(type="list", elements="str", required=False),
        application_ids=dict(type="list", elements="str", required=False),
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
