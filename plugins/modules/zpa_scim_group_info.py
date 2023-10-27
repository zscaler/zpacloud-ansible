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

    # Efficiently retrieve the idp_id and handle the case where idp_name is not found
    idp_id = next(
        (
            idp.get("id")
            for idp in client.idp.list_idps()
            if idp.get("name") == idp_name
        ),
        None,
    )
    if not idp_id:
        module.fail_json(msg=f"IdP with name '{idp_name}' not found")

    # Optimized search using scim_group_name
    if scim_group_name:
        scim_group = client.scim_groups.search_group(
            idp_id, scim_group_name
        )  # Adjusted parameters
        if not scim_group:
            module.fail_json(
                msg=f"Failed to retrieve SCIM Group Name: '{scim_group_name}'"
            )
        module.exit_json(changed=False, data=[scim_group])

    # Handling the case when scim_group_id is provided
    if scim_group_id is not None:
        attribute_box = client.scim_groups.get_group(group_id=scim_group_id)
        if attribute_box is None:
            module.fail_json(msg=f"Failed to retrieve SCIM group ID: '{scim_group_id}'")
        module.exit_json(changed=False, data=[attribute_box.to_dict()])

    # Fallback: List all groups if specific group is not provided
    scim_groups = client.scim_groups.list_groups(idp_id=idp_id).to_list()
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
