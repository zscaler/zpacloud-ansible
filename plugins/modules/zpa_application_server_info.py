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
module: zpa_application_server_info
short_description: Retrieve an application server information.
description:
    - This module will allow the retrieval of information about an application server.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

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

EXAMPLES = r"""
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

RETURN = r"""
servers:
  description: >-
    A list of dictionaries containing details about the specified Application Server(s).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Application Server.
      type: str
      sample: "216199618143442003"
    name:
      description: The name of the Application Server.
      type: str
      sample: "server1.acme.com"
    address:
      description: The address of the Application Server.
      type: str
      sample: "server1.acme.com"
    description:
      description: A description of the Application Server.
      type: str
      sample: "server1.acme.com"
    config_space:
      description: The configuration space of the Application Server.
      type: str
      sample: "DEFAULT"
    enabled:
      description: Indicates whether the Application Server is enabled.
      type: bool
      sample: true
    creation_time:
      description: The timestamp when the Application Server was created.
      type: str
      sample: "1724114751"
    modified_time:
      description: The timestamp when the Application Server was last modified.
      type: str
      sample: "1724114751"
    modified_by:
      description: The ID of the user who last modified the Application Server.
      type: str
      sample: "216199618143191041"

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)

    server_id = module.params.get("id")
    server_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    if server_id:
        result, _, error = client.servers.get_server(server_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Application Server ID '{server_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, groups=[result.as_dict()])

    # If no ID, we fetch all
    server_list, err = collect_all_items(client.servers.list_servers, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving Application Servers: {to_native(err)}")

    result_list = [g.as_dict() for g in server_list]

    if server_name:
        matched = next((g for g in result_list if g.get("name") == server_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Application Server '{server_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, groups=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
