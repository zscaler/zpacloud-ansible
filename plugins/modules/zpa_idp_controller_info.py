#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_idp_controller_info
short_description: Retrieves Identity Provider information.
description:
  - This module will allow the retrieval of information about an Identity Provider (IdP) detail from the ZPA Cloud.
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
      - Name of the Identity Provider.
    required: false
    type: str
  id:
    description:
      - ID of the Identity Provider.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All IdP Controllers
  zscaler.zpacloud.zpa_idp_controller_info:

- name: Get Details of a Specific IdP Controller by Name
  zscaler.zpacloud.zpa_idp_controller_info:
    name: User_IdP_Name

- name: Get Details of a Specific IdP Controller by ID
  zscaler.zpacloud.zpa_idp_controller_info:
    id: "216196257331282583"
"""

RETURN = """
# Returns information on a specified Identity Provider.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module: AnsibleModule):
    idp_id = module.params.get("id", None)
    idp_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    idps = []
    if idp_id is not None:
        idp_box = client.idp.get_idp(idp_id=idp_id)
        if idp_box is None:
            module.fail_json(
                msg="Failed to retrieve Identity Provider ID: '%s'" % (idp_id)
            )
        idps = [idp_box.to_dict()]
    else:
        idps = client.idp.list_idps().to_list()
        if idp_name is not None:
            idp_found = False
            for idp in idps:
                if idp.get("name") == idp_name:
                    idp_found = True
                    idps = [idp]
            if not idp_found:
                module.fail_json(
                    msg="Failed to retrieve Identity Provider Name: '%s'" % (idp_name)
                )
    module.exit_json(changed=False, data=idps)


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
