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
module: zpa_cloud_connector_group_info
short_description: Retrieves cloud connector group information.
description:
  - This module will allow the retrieval of information about a cloud connector group.
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)

    group_id = module.params.get("id")
    group_name = module.params.get("name")

    query_params = {}

    if group_id:
        result, _unused, error = (
            client.cloud_connector_groups.get_cloud_connector_groups(
                group_id, query_params
            )
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Cloud Connector ID '{group_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, groups=[result.as_dict()])

    # If no ID, we fetch all
    cert_list, err = collect_all_items(
        client.cloud_connector_groups.list_cloud_connector_groups, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving Cloud Connectors: {to_native(err)}")

    result_list = [g.as_dict() for g in cert_list]

    if group_name:
        matched = next((g for g in result_list if g.get("name") == group_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Cloud Connector '{group_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, groups=result_list)


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
