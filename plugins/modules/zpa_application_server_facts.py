#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_application_server_facts
short_description: Retrieve an application server information.
description:
    - This module will allow the retrieval of information about an application server.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider

options:
  name:
    description:
     - Name of the server group.
    required: false
    type: str
  id:
    description:
     - ID of the server group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Gather Information Details of All Application Servers
  zscaler.zpacloud.zpa_application_server_facts:
    provider: "{{ zpa_cloud }}"

- name: Gather Information Details of an Application Server by Name
  zscaler.zpacloud.zpa_application_server_facts:
      provider: "{{ zpa_cloud }}"
      name: server1.acme.com

- name: Gather Information Details of an Application Server by ID
  zscaler.zpacloud.zpa_application_server_facts:
      provider: "{{ zpa_cloud }}"
      id: "216196257331291921"

"""

RETURN = """
# Returns information on a specified Application Server.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    server_id = module.params.get("id", None)
    server_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    servers = []
    if server_id is not None:
        server_box = client.servers.get_server(server_id=server_id)
        if server_box is None:
            module.fail_json(
                msg="Failed to retrieve Application Server ID: '%s'" % (server_id)
            )
        servers = [server_box.to_dict()]
    else:
        servers = client.servers.list_servers().to_list()
        if server_name is not None:
            server_found = False
            for server in servers:
                if server.get("name") == server_name:
                    server_found = True
                    servers = [server]
            if not server_found:
                module.fail_json(
                    msg="Failed to retrieve Application Server Name: '%s'"
                    % (server_name)
                )
    module.exit_json(changed=False, data=servers)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
