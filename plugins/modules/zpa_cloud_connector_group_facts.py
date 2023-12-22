#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_cloud_connector_group_facts
short_description: Retrieves cloud connector group information.
description:
  - This module will allow the retrieval of information about a cloud connector group.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
options:
  name:
    description:
      - Name of the Cloud Connector Group.
    required: false
    type: str
  id:
    description:
      - ID of the Cloud Connector Group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information Details of All Cloud Connector Groups
  zscaler.zpacloud.zpa_cloud_connector_group_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Information Details of a Cloud Connector Group by Name
  zscaler.zpacloud.zpa_cloud_connector_group_facts:
    provider: "{{ zpa_cloud }}"
    name: zs-cc-vpc-096108eb5d9e68d71-ca-central-1a

- name: Get Information Details of a Cloud Connector Group by ID
  zscaler.zpacloud.zpa_cloud_connector_group_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331292017"
"""

RETURN = """
# Returns information on a specified Cloud Connector Group.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    group_id = module.params.get("id", None)
    group_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    groups = []
    if group_id is not None:
        group_box = client.cloud_connector_groups.get_group(group_id=group_id)
        if group_box is None:
            module.fail_json(
                msg="Failed to retrieve Cloud Connector Group ID: '%s'" % (group_id)
            )
        groups = [group_box.to_dict()]
    else:
        groups = client.cloud_connector_groups.list_groups().to_list()
        if group_name is not None:
            group_found = False
            for group in groups:
                if group.get("name") == group_name:
                    group_found = True
                    groups = [group]
            if not group_found:
                module.fail_json(
                    msg="Failed to retrieve Cloud Connector Group Name: '%s'"
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
