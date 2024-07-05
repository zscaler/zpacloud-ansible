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
module: zpa_lss_config_controller_facts
short_description: Retrieves LSS Config controller information.
description:
  - This module will allow the retrieval of information about a LSS Config controlle.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
      - Name of the LSS Config controlle.
    required: false
    type: str
  id:
    description:
      - ID of the LSS Config controlle.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information Details of All Cloud lss_configs
  zscaler.zpacloud.zpa_lss_config_controller_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Information Details of a LSS Config controlle by Name
  zscaler.zpacloud.zpa_lss_config_controller_facts:
    provider: "{{ zpa_cloud }}"
    name: Example_LSS_Config_Controller

- name: Get Information Details of a LSS Config controlle by ID
  zscaler.zpacloud.zpa_lss_config_controller_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331292017"
"""

RETURN = """
# Returns information on a specified LSS Config controlle.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    lss_config_name = module.params.get("name", None)
    lss_config_id = module.params.get("id", None)
    client = ZPAClientHelper(module)
    lss_configs = []
    if lss_config_id is not None:
        lss_config = client.lss.get_config(lss_id=lss_config_id)
        if lss_config is None:
            module.fail_json(msg="Failed to retrieve lss_config ID: '%s'" % (id))
        lss_configs = [lss_config]
    elif lss_config_name is not None:
        lss_configs_ = client.lss.list_configs(pagesize=500).to_list()
        found = False
        for k in lss_configs_:
            if k.get("config").get("name") == lss_config_name:
                lss_configs = [k]
                found = True
                break
        if not found:
            module.fail_json(
                msg="Failed to retrieve lss_config Name: '%s'" % (lss_config_name)
            )
    else:
        lss_configs = client.lss.list_configs().to_list()
    module.exit_json(changed=False, data=lss_configs)


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
