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
module: zpa_pra_credential_controller_info
short_description: Retrieves information about a PRA Credential.
description:
    - This module will allow the retrieval of information about a PRA Credential.
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
    description: "The unique identifier of the privileged credential"
    required: false
  name:
    type: str
    description: "The name of the privileged credential"
    required: false
"""

EXAMPLES = """
- name: Get Detail Information of All PRA Credentials
  zscaler.zpacloud.zpa_pra_credential_controller_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a PRA Credential by Name
  zscaler.zpacloud.zpa_pra_credential_controller_info:
    provider: "{{ zpa_cloud }}"
    name: "Example"

- name: Get Details of a PRA Credential by ID
  zscaler.zpacloud.zpa_pra_credential_controller_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
creds:
  description: >-
    A list of dictionaries containing details about the specified PRA Credential(s).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the PRA Credential.
      type: str
      sample: "8530"
    name:
      description: The name of the PRA Credential.
      type: str
      sample: "credential01"
    description:
      description: A description of the PRA Credential.
      type: str
      sample: "credential01"
    credential_type:
      description: The type of the PRA Credential.
      type: str
      sample: "USERNAME_PASSWORD"
    user_name:
      description: The user name associated with the PRA Credential.
      type: str
      sample: "jdoe"
    user_domain:
      description: The user domain associated with the PRA Credential.
      type: str
      sample: "acme.com"
    creation_time:
      description: The timestamp when the PRA Credential was created.
      type: str
      sample: "1724113778"
    modified_time:
      description: The timestamp when the PRA Credential was last modified.
      type: str
      sample: "1724113778"
    last_credential_reset_time:
      description: The timestamp when the PRA Credential was last reset.
      type: str
      sample: "1724113778"
    modified_by:
      description: The ID of the user who last modified the PRA Credential.
      type: str
      sample: "216199618143191041"
    microtenant_name:
      description: The name of the microtenant associated with the PRA Credential.
      type: str
      sample: "Default"

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
    credential_id = module.params.get("id", None)
    cred_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    creds = []
    if credential_id is not None:
        cred_box = client.privileged_remote_access.get_credential(
            credential_id=credential_id
        )
        if cred_box is None:
            module.fail_json(
                msg="Failed to retrieve PRA Credential ID: '%s'" % (credential_id)
            )
        creds = [cred_box.to_dict()]
    else:
        creds = client.privileged_remote_access.list_credentials(pagesize=500).to_list()
        if cred_name is not None:
            cred_found = False
            for cred in creds:
                if cred.get("name") == cred_name:
                    cred_found = True
                    creds = [cred]
            if not cred_found:
                module.fail_json(
                    msg="Failed to retrieve PRA Credential Name: '%s'" % (cred_name)
                )
    module.exit_json(changed=False, creds=creds)


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
