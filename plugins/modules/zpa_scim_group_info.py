#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_scim_group_info
short_description: Retrieves scim group information from a given IDP
description:
  - This module will allow the retrieval of information about scim group(s) from a given IDP
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
      - Name of the scim group.
    required: false
    type: str
  idp_name:
    description:
      - Name of the IDP.
    required: true
    type: str
  id:
    description:
      - ID of the scim group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All SCIM Groups from an IdP
  zscaler.zpacloud.zpa_scim_attribute_header_info:
    idp_name: "IdP_Name"
- name: Get Information About a SCIM Group by ID
  zscaler.zpacloud.zpa_scim_attribute_header_info:
    id: 216196257331285827
    idp_name: "IdP_Name"
- name: Get Information About a SCIM Group by Name
  zscaler.zpacloud.zpa_scim_attribute_header_info:
    name: "Finance"
    idp_name: "IdP_Name"
"""

RETURN = """
# Returns information on a specified posture profile.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    scim_group_name = module.params.get("name", None)
    scim_group_id = module.params.get("id", None)
    idp_name = module.params.get("idp_name", None)
    client = ZPAClientHelper(module)
    scim_groups = []
    if scim_group_id is not None:
        attribute_box = client.scim_groups.get_group(group_id=scim_group_id)
        if attribute_box is None:
            module.fail_json(msg="Failed to retrieve scim group ID: '%s'" % (id))
        scim_groups = [attribute_box.to_dict()]
    else:
        idp_id = ""
        idps = client.idp.list_idps()
        for idp in idps:
            if idp.get("name") == idp_name:
                idp_id = idp.get("id")
        scim_groups = client.scim_groups.list_groups(idp_id=idp_id).to_list()
        if scim_group_name is not None:
            scim_group_found = False
            for scim_group in scim_groups:
                if scim_group.get("name") == scim_group_name:
                    scim_group_found = True
                    scim_groups = [scim_group]
            if not scim_group_found:
                module.fail_json(
                    msg="Failed to retrieve App Connector Group Name: '%s'"
                    % (scim_group_name)
                )
    module.exit_json(changed=False, data=scim_groups)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        idp_name=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
