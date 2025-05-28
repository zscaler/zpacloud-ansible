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
module: zpa_pra_portal_controller_info
short_description: Retrieves information about a PRA Portal.
description:
    - This module will allow the retrieval of information about a PRA Portal.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  id:
    type: str
    description: "The unique identifier of the privileged portal"
    required: false
  name:
    type: str
    description: "The name of the privileged portal"
    required: false
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Detail Information of All PRA Portal
  zscaler.zpacloud.zpa_pra_portal_controller_info:
    provider: '{{ zpa_cloud }}'

- name: Get Details of a PRA Portal by Name
  zscaler.zpacloud.zpa_pra_portal_controller_info:
    provider: '{{ zpa_cloud }}'
    name: "Example"

- name: Get Details of a PRA Portal by ID
  zscaler.zpacloud.zpa_pra_portal_controller_info:
    provider: '{{ zpa_cloud }}'
    id: "216196257331291969"
"""

RETURN = """
portals:
  description: Information about the PRA Portals.
  returned: always
  type: list
  elements: dict
  contains:
    c_name:
      description: The canonical name of the portal.
      type: str
      sample: "216199618143442004.********.pra.p.zpa-app.net"
    certificate_id:
      description: The ID of the certificate associated with the portal.
      type: str
      sample: "216199618143247243"
    certificate_name:
      description: The name of the certificate associated with the portal.
      type: str
      sample: "jenkins.bd-hashicorp.com"
    creation_time:
      description: The timestamp when the portal was created.
      type: str
      sample: "1724115556"
    description:
      description: A description of the portal.
      type: str
      sample: "portal.acme.com"
    domain:
      description: The domain associated with the portal.
      type: str
      sample: "portal.acme.com"
    enabled:
      description: Indicates whether the portal is enabled.
      type: bool
      sample: true
    id:
      description: The unique identifier of the portal.
      type: str
      sample: "216199618143442004"
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
      sample: "1724115556"
    name:
      description: The name of the portal.
      type: str
      sample: "portal.acme.com"
    user_notification:
      description: The user notification associated with the portal.
      type: str
      sample: "portal.acme.com"
    user_notification_enabled:
      description: Indicates whether user notifications are enabled for the portal.
      type: bool
      sample: true

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
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
        result, _unused, error = client.pra_portal.get_portal(portal_id, query_params)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve PRA Portal ID '{portal_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, portals=[result.as_dict()])

    # Warn log before pagination call
    module.warn(f"[PRA Portal] Fetching all portals with query_params: {query_params}")

    # If no ID, we fetch all
    portal_list, err = collect_all_items(client.pra_portal.list_portals, query_params)
    if err:
        module.fail_json(msg=f"Error retrieving PRA Portals: {to_native(err)}")

    module.warn(f"[PRA Portal] Total portals retrieved: {len(portal_list)}")

    result_list = [g.as_dict() for g in portal_list]

    if portal_name:
        matched = next((g for g in result_list if g.get("name") == portal_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"PRA Portal '{portal_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, portals=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
