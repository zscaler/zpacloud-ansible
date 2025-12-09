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
module: zpa_user_portal_controller_info
short_description: Retrieves information about a User Portal Controller.
description:
    - This module will allow the retrieval of information about a User Portal Controller.
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
     - Name of the User Portal Controller.
    required: false
    type: str
  id:
    description:
     - ID of the User Portal Controller.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Detail Information of All User Portal Controllers
  zscaler.zpacloud.zpa_user_portal_controller_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a User Portal Controller by Name
  zscaler.zpacloud.zpa_user_portal_controller_info:
    provider: "{{ zpa_cloud }}"
    name: "UserPortal01"

- name: Get Details of a User Portal Controller by ID
  zscaler.zpacloud.zpa_user_portal_controller_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
portals:
  description: >-
    A list of dictionaries containing details about the User Portal Controllers.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the User Portal Controller.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the User Portal Controller.
      type: str
      sample: "UserPortal01"
    description:
      description: A brief description of the User Portal Controller.
      type: str
      sample: "User Portal for corporate access"
    enabled:
      description: Indicates whether the User Portal Controller is enabled.
      type: bool
      sample: true
    certificate_id:
      description: Certificate ID for the User Portal Controller.
      type: str
      sample: "216199618143191041"
    certificate_name:
      description: Certificate name for the User Portal Controller.
      type: str
      sample: "portal_cert"
    domain:
      description: Domain for the User Portal Controller.
      type: str
      sample: "portal.example.com"
    ext_domain:
      description: External domain for the User Portal Controller.
      type: str
      sample: "ext.portal.example.com"
    ext_domain_name:
      description: External domain name for the User Portal Controller.
      type: str
      sample: "ext-portal-example.zscalerportal.net"
    ext_domain_translation:
      description: External domain translation for the User Portal Controller.
      type: str
      sample: "ext.portal.example.com"
    ext_label:
      description: External label for the User Portal Controller.
      type: str
      sample: "portal01"
    getc_name:
      description: GETC name for the User Portal Controller.
      type: str
      sample: "getc_portal"
    image_data:
      description: Image data for the User Portal Controller.
      type: str
      sample: "base64encodedimage"
    user_notification:
      description: User notification message for the User Portal Controller.
      type: str
      sample: "Welcome to the corporate portal"
    user_notification_enabled:
      description: Whether user notifications are enabled for the User Portal Controller.
      type: bool
      sample: true
    managed_by_zs:
      description: Whether the User Portal Controller is managed by Zscaler.
      type: bool
      sample: false
    microtenant_id:
      description: The unique identifier of the microtenant associated with the portal.
      type: str
      sample: "216199618143191041"
    microtenant_name:
      description: The name of the microtenant associated with the portal.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the portal.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the portal was last modified.
      type: str
      sample: "1724111641"
    creation_time:
      description: The timestamp when the portal was created.
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

    portal_id = module.params.get("id")
    portal_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    if portal_id:
        result, _unused, error = client.user_portal_controller.get_user_portal(portal_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve User Portal Controller ID '{portal_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, portals=[result.as_dict()])

    # If no ID, we fetch all
    portal_list, err = collect_all_items(client.user_portal_controller.list_user_portals, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving User Portal Controllers: {to_native(err)}")

    result_list = [p.as_dict() for p in portal_list]

    if portal_name:
        matched = next((p for p in result_list if p.get("name") == portal_name), None)
        if not matched:
            available = [p.get("name") for p in result_list]
            module.fail_json(
                msg=f"User Portal Controller '{portal_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, portals=result_list)


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

