#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_lss_config_controller_info
short_description: Retrieves LSS Config controller information.
description:
  - This module will allow the retrieval of information about a LSS Config controlle.
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
  zscaler.zpacloud.zpa_lss_config_controller_info:

- name: Get Information Details of a LSS Config controlle by Name
  zscaler.zpacloud.zpa_lss_config_controller_info:
    name: zs-cc-vpc-096108eb5d9e68d71-ca-central-1a

- name: Get Information Details of a LSS Config controlle by ID
  zscaler.zpacloud.zpa_lss_config_controller_info:
    id: "216196257331292017"
"""

RETURN = """
# Returns information on a specified LSS Config controlle.
"""

from re import T
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
        lss_configs_ = client.lss.list_configs().to_list()
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
