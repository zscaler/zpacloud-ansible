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
module: zpa_pra_console_controller_info
short_description: Retrieves information about a PRA Console.
description:
    - This module will allow the retrieval of information about a PRA Console.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  id:
    type: str
    description: "The unique identifier of the privileged Console"
    required: false
  name:
    type: str
    description: "The name of the privileged Console"
    required: false
"""

EXAMPLES = """
- name: Get Detail Information of All PRA Consoles
  zscaler.zpacloud.zpa_pra_console_controller_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a PRA Console by Name
  zscaler.zpacloud.zpa_pra_console_controller_info:
    provider: "{{ zpa_cloud }}"
    name: "Example"

- name: Get Details of a PRA Console by ID
  zscaler.zpacloud.zpa_pra_console_controller_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = """
# Returns information on a specified pra console.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    console_id = module.params.get("id", None)
    console_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    consoles = []
    if console_id is not None:
        console_box = client.privileged_remote_access.get_console(console_id=console_id)
        if console_box is None:
            module.fail_json(
                msg="Failed to retrieve PRA Console ID: '%s'" % (console_id)
            )
        consoles = [console_box.to_dict()]
    else:
        consoles = client.privileged_remote_access.list_consoles(pagesize=500).to_list()
        if console_name is not None:
            console_found = False
            for console in consoles:
                if console.get("name") == console_name:
                    console_found = True
                    consoles = [console]
            if not console_found:
                module.fail_json(
                    msg="Failed to retrieve PRA Console Name: '%s'" % (console_name)
                )
    module.exit_json(changed=False, consoles=consoles)


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
