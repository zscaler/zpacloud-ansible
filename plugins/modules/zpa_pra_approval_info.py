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
module: zpa_pra_approval_info
short_description: Retrieves information about a PRA Approval.
description:
    - This module will allow the retrieval of information about a PRA Approval.
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
  email_id:
    description: The email address of the user that you are assigning the privileged approval to.
    type: str
    required: false
  sort_dir:
    type: str
    description: Specifies the sort direction (i.e., ascending or descending order).
    required: false
    choices:
      - ASC
      - DESC
  sort_by:
    type: str
    description: The sort string used to support sorting on the given field for the API.
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

    approval_id = module.params.get("id")
    email_id = module.params.get("email_id")
    microtenant_id = module.params.get("microtenant_id")
    sort_by = module.params.get("sort_by")
    sort_dir = module.params.get("sort_dir")

    # Construct query parameters
    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id
    if sort_by:
        query_params["sort_by"] = sort_by
    if sort_dir:
        query_params["sort_dir"] = sort_dir

    # 🔥 Strict search syntax: "emailIds+EQ+<email>"
    if email_id:
        query_params["search"] = f"emailIds+EQ+{email_id}"

    # Lookup by ID
    if approval_id:
        result, _unused, error = client.pra_approval.get_approval(
            approval_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve PRA Approval ID '{approval_id}': {to_native(error)}"
            )
        module.exit_json(
            changed=False,
            data=[result.as_dict() if hasattr(result, "as_dict") else result],
        )

    # Fetch all (filtered or not)
    module.warn(
        f"[PRA Approval] Fetching all approvals with query_params: {query_params}"
    )
    approval_list, err = collect_all_items(
        client.pra_approval.list_approval, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving PRA Approvals: {to_native(err)}")

    module.warn(f"[PRA Approval] Total approvals retrieved: {len(approval_list)}")

    result_list = [a.as_dict() if hasattr(a, "as_dict") else a for a in approval_list]
    module.exit_json(changed=False, data=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        email_id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        sort_by=dict(type="str", required=False),
        sort_dir=dict(type="str", required=False, choices=["ASC", "DESC"]),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
