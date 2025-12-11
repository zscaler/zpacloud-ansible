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
module: zpa_user_portal_aup_info
short_description: Retrieves information about a User Portal Acceptable Use Policy (AUP).
description:
    - This module will allow the retrieval of information about a User Portal Acceptable Use Policy (AUP).
    - The AUP defines the terms and conditions that users must accept when accessing the portal.
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
     - Name of the User Portal AUP.
    required: false
    type: str
  id:
    description:
     - ID of the User Portal AUP.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Detail Information of All User Portal AUPs
  zscaler.zpacloud.zpa_user_portal_aup_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a User Portal AUP by Name
  zscaler.zpacloud.zpa_user_portal_aup_info:
    provider: "{{ zpa_cloud }}"
    name: "Standard AUP"

- name: Get Details of a User Portal AUP by ID
  zscaler.zpacloud.zpa_user_portal_aup_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
aups:
  description: >-
    A list of dictionaries containing details about the User Portal AUPs.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the User Portal AUP.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the User Portal AUP.
      type: str
      sample: "Standard AUP"
    description:
      description: A brief description of the User Portal AUP.
      type: str
      sample: "Standard Acceptable Use Policy for all users"
    enabled:
      description: Indicates whether the User Portal AUP is enabled.
      type: bool
      sample: true
    aup:
      description: The Acceptable Use Policy text content that users must accept.
      type: str
      sample: "By accessing this portal, you agree to comply with all company policies..."
    email:
      description: Contact email address for the AUP.
      type: str
      sample: "admin@example.com"
    phone_num:
      description: Contact phone number for the AUP.
      type: str
      sample: "+1-555-123-4567"
    microtenant_id:
      description: The unique identifier of the microtenant associated with the AUP.
      type: str
      sample: "216199618143191041"
    microtenant_name:
      description: The name of the microtenant associated with the AUP.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the AUP.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the AUP was last modified.
      type: str
      sample: "1724111641"
    creation_time:
      description: The timestamp when the AUP was created.
      type: str
      sample: "1724111641"
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

    aup_id = module.params.get("id")
    aup_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    if aup_id:
        result, _unused, error = client.user_portal_aup.get_user_portal_aup(aup_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve User Portal AUP ID '{aup_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, aups=[result.as_dict()])

    # If no ID, we fetch all
    aup_list, err = collect_all_items(client.user_portal_aup.list_user_portal_aup, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving User Portal AUPs: {to_native(err)}")

    result_list = [a.as_dict() for a in aup_list]

    if aup_name:
        matched = next((a for a in result_list if a.get("name") == aup_name), None)
        if not matched:
            available = [a.get("name") for a in result_list]
            module.fail_json(
                msg=f"User Portal AUP '{aup_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, aups=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
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
