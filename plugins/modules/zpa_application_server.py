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
module: zpa_application_server
short_description: Create an application server in the ZPA Cloud.
description:
    - This module creates/update/delete an application server in the ZPA Cloud.
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
    name:
        description:
            - This field defines the name of the server to create.
        required: True
        type: str
    id:
        description: ""
        required: false
        type: str
    address:
        description: ""
        required: true
        type: str
    app_server_group_ids:
        description:
            - This field defines the list of server groups IDs.
        required: False
        type: list
        elements: str
    enabled:
        description:
            - This field defines the status of the server, true or false.
        required: False
        type: bool
    description:
        description:
            - This field defines the description of the server to create.
        required: False
        type: str
    config_space:
        description:
            - This field defines the type of the server, DEFAULT or SIEM.
        required: False
        type: str
        default: "DEFAULT"
        choices: ["DEFAULT", "SIEM"]
    state:
        description: "Whether the app should be present or absent."
        type: str
        choices:
            - present
            - absent
        default: present
"""

EXAMPLES = """
- name: Create Second Application Server
  zscaler.zpacloud.zpa_application_server:
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    deleteNone,
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    server = dict()
    params = [
        "id",
        "name",
        "description",
        "address",
        "enabled",
        "app_server_group_ids",
        "config_space",
    ]
    for param_name in params:
        server[param_name] = module.params.get(param_name, None)
    server_id = server.get("id", None)
    server_name = server.get("name", None)
    existing_server = None
    if server_id is not None:
        server_box = client.servers.get_server(server_id=server_id)
        if server_box is not None:
            existing_server = server_box.to_dict()
    elif server_name is not None:
        servers = client.servers.list_servers().to_list()
        for server_ in servers:
            if server_.get("name") == server_name:
                existing_server = server_
    if existing_server is not None:
        id = existing_server.get("id")
        existing_server.update(server)
        existing_server["id"] = id
    if state == "present":
        if existing_server is not None:
            """Update"""
            existing_server = deleteNone(
                dict(
                    server_id=existing_server.get("id"),
                    name=existing_server.get("name"),
                    description=existing_server.get("description"),
                    address=existing_server.get("address"),
                    enabled=existing_server.get("enabled"),
                    app_server_group_ids=existing_server.get("app_server_group_ids"),
                    config_space=existing_server.get("config_space"),
                )
            )
            existing_server = client.servers.update_server(**existing_server).to_dict()
            module.exit_json(changed=True, data=existing_server)
        else:
            """Create"""
            server = deleteNone(
                dict(
                    name=server.get("name"),
                    description=server.get("description"),
                    address=server.get("address"),
                    enable=server.get("enable"),
                    app_server_group_ids=server.get("app_server_group_ids"),
                    config_space=server.get("config_space"),
                )
            )
            server = client.servers.add_server(**server).to_dict()
            module.exit_json(changed=True, data=server)
    elif (
        state == "absent"
        and existing_server is not None
        and existing_server.get("id") is not None
    ):
        code = client.servers.delete_server(server_id=existing_server.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_server)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        address=dict(type="str", required=True),
        enabled=dict(type="bool", required=False),
        app_server_group_ids=dict(type="list", elements="str", required=False),
        config_space=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
