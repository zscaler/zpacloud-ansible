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


def core(module):
    portal_id = module.params.get("id", None)
    portal_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    portals = []
    if portal_id is not None:
        portal_box = client.privileged_remote_access.get_portal(portal_id=portal_id)
        if portal_box is None:
            module.fail_json(msg="Failed to retrieve PRA Portal ID: '%s'" % (portal_id))
        portals = [portal_box.to_dict()]
    else:
        portals = client.privileged_remote_access.list_portals(pagesize=500).to_list()
        if portal_name is not None:
            portal_found = False
            for portal in portals:
                if portal.get("name") == portal_name:
                    portal_found = True
                    portals = [portal]
            if not portal_found:
                module.fail_json(
                    msg="Failed to retrieve PRA Portal Name: '%s'" % (portal_name)
                )
    module.exit_json(changed=False, portals=portals)


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
