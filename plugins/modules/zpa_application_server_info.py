#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_application_server_info
short_description: Retrieve an application server information.
description:
    - This module will allow the retrieval of information about an application server.
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
  zscaler.zpacloud.zpa_application_server_info:

- name: Gather Information Details of an Application Server by Name
  zscaler.zpacloud.zpa_application_server_info:
      name: server1.acme.com

- name: Gather Information Details of an Application Server by ID
  zscaler.zpacloud.zpa_application_server_info:
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


def core(module: AnsibleModule):
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
