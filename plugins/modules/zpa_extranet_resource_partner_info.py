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
module: zpa_extranet_resource_partner_info
short_description: Retrieves information about an Extranet Resource Partner.
description:
    - This module will allow the retrieval of information about an Extranet Resource Partner.
    - Extranet Resource Partners represent external resources that can be accessed through ZPA.
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
     - Name of the Extranet Resource Partner.
    required: false
    type: str
  id:
    description:
     - ID of the Extranet Resource Partner.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Detail Information of All Extranet Resource Partners
  zscaler.zpacloud.zpa_extranet_resource_partner_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of an Extranet Resource Partner by Name
  zscaler.zpacloud.zpa_extranet_resource_partner_info:
    provider: "{{ zpa_cloud }}"
    name: "Partner_ER"

- name: Get Details of an Extranet Resource Partner by ID
  zscaler.zpacloud.zpa_extranet_resource_partner_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
partners:
  description: >-
    A list of dictionaries containing details about the Extranet Resource Partners.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Extranet Resource Partner.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the Extranet Resource Partner.
      type: str
      sample: "Partner_ER"
    enabled:
      description: Indicates whether the Extranet Resource Partner is enabled.
      type: bool
      sample: true
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

    partner_id = module.params.get("id")
    partner_name = module.params.get("name")

    query_params = {}

    # Fetch all extranet resource partners
    partner_list, err = collect_all_items(
        client.extranet_resource.list_extranet_resources_partner, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving Extranet Resource Partners: {to_native(err)}")

    result_list = [p.as_dict() for p in partner_list]

    if partner_id:
        matched = next((p for p in result_list if p.get("id") == partner_id), None)
        if not matched:
            module.fail_json(
                msg=f"Extranet Resource Partner ID '{partner_id}' not found."
            )
        result_list = [matched]

    elif partner_name:
        matched = next((p for p in result_list if p.get("name") == partner_name), None)
        if not matched:
            available = [p.get("name") for p in result_list]
            module.fail_json(
                msg=f"Extranet Resource Partner '{partner_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, partners=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["id", "name"]],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
