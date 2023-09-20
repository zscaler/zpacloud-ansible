#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_service_edge_groups_info
short_description: Retrieves information about a Service Edge Group.
description:
    - This module will allow the retrieval of information about a Service Edge Group resource.
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
      - Name of the Service Edge Group..
    required: false
    type: str
  id:
    description:
      - ID of the Service Edge Group..
    required: false
    type: str

"""

EXAMPLES = """
- name: Get information about all Service Edge Groups
  zscaler.zpacloud.zpa_service_edge_groups_info:
- name: Get information about Service Edge Connector Group by ID
  zscaler.zpacloud.zpa_service_edge_groups_info:
    id: "198288282"

- name: Get information about Service Edge Connector Group by Name
  zscaler.zpacloud.zpa_service_edge_groups_info:
    name: "Example"
"""

RETURN = """
# Returns information on a specified Service Edge Group.
"""


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module: AnsibleModule):
    group_id = module.params.get("id", None)
    group_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    groups = []
    if group_id is not None:
        group_box = client.service_edges.get_service_edge_group(group_id=group_id)
        if group_box is None:
            module.fail_json(
                msg="Failed to retrieve Service Edge Group ID: '%s'" % (group_id)
            )
        groups = [group_box.to_dict()]
    else:
        groups = client.service_edges.list_service_edge_groups().to_list()
        if group_name is not None:
            group_found = False
            for group in groups:
                if group.get("name") == group_name:
                    group_found = True
                    groups = [group]
            if not group_found:
                module.fail_json(
                    msg="Failed to retrieve Service Edge Group Name: '%s'"
                    % (group_name)
                )
    module.exit_json(changed=False, data=groups)


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
