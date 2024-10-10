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
module: zpa_service_edge_controller_info
short_description: Retrieves a service edge controller information
description:
  - This module will allow the retrieval of information about a service edge controller.
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
      - Name of the Service Edge Controller.
    required: false
    type: str
  id:
    description:
      - ID of the Service Edge Controller.
    required: false
    type: str
"""

EXAMPLES = """
- name: Retrieve All App Service Edge Controlles
  zscaler.zpacloud.zpa_service_edge_controller_info:
    provider: "{{ zpa_cloud }}"

- name: Retrieve Service Edge Controlle By Name
  zscaler.zpacloud.zpa_service_edge_controller_info:
    provider: "{{ zpa_cloud }}"
    name: 'SJC037_App_Connector'

- name: Retrieve Service Edge Controlle By ID
  zscaler.zpacloud.zpa_service_edge_controller_info:
    provider: "{{ zpa_cloud }}"
    name: '123456789'
"""

RETURN = """
# Default return values
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    service_edge_id = module.params.get("id", None)
    service_edge_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    pses = []
    if service_edge_id is not None:
        pse_box = client.service_edges.get_service_edge(service_edge_id=service_edge_id)
        if pse_box is None:
            module.fail_json(
                msg="Failed to retrieve Service Edge ID: '%s'" % (service_edge_id)
            )
        pses = [pse_box.to_dict()]
    else:
        pses = client.service_edges.list_service_edges(pagesize=500).to_list()
        if service_edge_name is not None:
            service_edge_found = False
            for pse in pses:
                if pse.get("name") == service_edge_name:
                    service_edge_found = True
                    pses = [pse]
            if not service_edge_found:
                module.fail_json(
                    msg="Failed to retrieve Service Edge Name: '%s'"
                    % (service_edge_name)
                )
    module.exit_json(changed=False, pses=pses)


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
