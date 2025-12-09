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
module: zpa_user_portal_link_info
short_description: Retrieves information about a User Portal Link.
description:
    - This module will allow the retrieval of information about a User Portal Link.
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
     - Name of the User Portal Link.
    required: false
    type: str
  id:
    description:
     - ID of the User Portal Link.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Detail Information of All User Portal Links
  zscaler.zpacloud.zpa_user_portal_link_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a User Portal Link by Name
  zscaler.zpacloud.zpa_user_portal_link_info:
    provider: "{{ zpa_cloud }}"
    name: "server1.example.com"

- name: Get Details of a User Portal Link by ID
  zscaler.zpacloud.zpa_user_portal_link_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
links:
  description: >-
    A list of dictionaries containing details about the User Portal Links.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the User Portal Link.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the User Portal Link.
      type: str
      sample: "server1.example.com"
    description:
      description: A brief description of the User Portal Link.
      type: str
      sample: "Portal link for accessing server1"
    enabled:
      description: Indicates whether the User Portal Link is enabled.
      type: bool
      sample: true
    application_id:
      description: Application ID associated with the User Portal Link.
      type: str
      sample: "216199618143191041"
    icon_text:
      description: Icon text for the User Portal Link.
      type: str
      sample: ""
    link:
      description: Link URL for the User Portal Link.
      type: str
      sample: "server1.example.com"
    link_path:
      description: Link path for the User Portal Link.
      type: str
      sample: ""
    protocol:
      description: Protocol for the User Portal Link.
      type: str
      sample: "https://"
    microtenant_id:
      description: The unique identifier of the microtenant associated with the link.
      type: str
      sample: "216199618143191041"
    user_portal_id:
      description: The user portal ID associated with the link.
      type: str
      sample: "216199618143191041"
    user_portals:
      description: List of user portals associated with the link.
      type: list
      elements: dict
      contains:
        id:
          description: The unique identifier of the user portal.
          type: str
          sample: "216199618143191041"
        name:
          description: The name of the user portal.
          type: str
          sample: "UserPortal01"
        enabled:
          description: Whether the user portal is enabled.
          type: bool
          sample: true
    modified_by:
      description: The ID of the user who last modified the link.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the link was last modified.
      type: str
      sample: "1724111641"
    creation_time:
      description: The timestamp when the link was created.
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

    link_id = module.params.get("id")
    link_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    if link_id:
        result, _unused, error = client.user_portal_link.get_portal_link(link_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve User Portal Link ID '{link_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, links=[result.as_dict()])

    # If no ID, we fetch all
    link_list, err = collect_all_items(client.user_portal_link.list_portal_link, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving User Portal Links: {to_native(err)}")

    result_list = [l.as_dict() for l in link_list]

    if link_name:
        matched = next((l for l in result_list if l.get("name") == link_name), None)
        if not matched:
            available = [l.get("name") for l in result_list]
            module.fail_json(
                msg=f"User Portal Link '{link_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, links=result_list)


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

