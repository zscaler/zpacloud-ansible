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
module: zpa_scim_group_facts
short_description: Retrieves scim group information from a given IDP
description:
  - This module will allow the retrieval of information about scim group(s) from a given IDP
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
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    idp_name: "IdP_Name"

- name: Get Information About a SCIM Group by ID
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    id: 216196257331285827
    idp_name: "IdP_Name"

- name: Get Information About a SCIM Group by Name
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
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
    scim_group_name = module.params.get("name")
    scim_group_id = module.params.get("id")
    idp_name = module.params.get("idp_name")
    client = ZPAClientHelper(module)

    # Get the IDP ID based on idp_name
    idp_id = next(
        (
            idp.get("id")
            for idp in client.idp.list_idps()
            if idp.get("name") == idp_name
        ),
        None,
    )
    if not idp_id:
        module.fail_json(msg=f"IDP with name '{idp_name}' not found")

    if scim_group_id:
        # Fetch group by ID
        group = client.scim_groups.get_group(group_id=scim_group_id)
        if not group:
            module.fail_json(msg=f"SCIM group with ID '{scim_group_id}' not found")
        module.exit_json(changed=False, data=[group.to_dict()])

    if scim_group_name:
        # Fetch groups and filter by name
        all_groups = client.scim_groups.list_groups(
            idp_id=idp_id, search=scim_group_name
        )
        group = next((g for g in all_groups if g.get("name") == scim_group_name), None)
        if not group:
            module.fail_json(msg=f"SCIM group with name '{scim_group_name}' not found")
        module.exit_json(changed=False, data=[group])

    # If no specific group ID or name is provided, list all groups
    all_groups = client.scim_groups.list_groups(idp_id=idp_id)
    module.exit_json(changed=False, data=[g.to_dict() for g in all_groups])


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
