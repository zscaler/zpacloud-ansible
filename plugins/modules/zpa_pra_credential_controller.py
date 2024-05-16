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
module: zpa_pra_credential_controller
short_description: Create a PRA Credential.
description:
  - This module will create/update/delete Privileged Remote Access Credential.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  id:
    type: str
    description: "The unique identifier of the privileged credential"
    required: false
  name:
    type: str
    description: "The name of the privileged credential"
    required: true
  description:
    type: str
    description: "The description of the privileged credential"
    required: false
  credential_type:
    type: str
    description:
        - The protocol type that was designated for that particular privileged credential.
        - The protocol type options are SSH, RDP, and VNC.
        - Each protocol type has its own credential requirements
    required: false
    choices:
        - USERNAME_PASSWORD
        - SSH_KEY
        - PASSWORD
  passphrase:
    type: str
    description:
        - The password that is used to protect the SSH private key
        - This field is optional
    required: false
  password:
    type: str
    description:
        - The password associated with the username for the login you want to use for the privileged credential
    required: false
  private_key:
    type: str
    description:
        - The SSH private key associated with the username for the login you want to use for the privileged credential
    required: false
  user_domain:
    type: str
    description:
        - The domain name associated with the username
        - You can also include the domain name as part of the username
        - The domain name only needs to be specified with logging in to an RDP console that is connected to an Active Directory Domain
    required: false
  username:
    type: str
    description:
        - The username for the login you want to use for the privileged credential
    required: false
"""

EXAMPLES = """
- name: Create/Update/Delete PRA Credentials
  zscaler.zpacloud.zpa_pra_credential_controller:
    provider: "{{ zpa_cloud }}"
    name: John Doe
    description: Created with Ansible
    credential_type: USERNAME_PASSWORD
    user_domain: acme.com
    username: jdoe
    password: ''
  register: result
"""

RETURN = """
# The newly created privileged credentials resource record.
"""


def normalize_creds(cred):
    """
    Normalize credential data by setting computed values.
    """
    normalized = cred.copy()

    computed_values = [
        "id",
        "password",
        "private_key",
        "passphrase",
        "username",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    cred = dict()
    params = [
        "id",
        "name",
        "description",
        "credential_type",
        "passphrase",
        "password",
        "private_key",
        "user_domain",
        "username",
        "username",
    ]
    for param_name in params:
        cred[param_name] = module.params.get(param_name, None)
    credential_id = cred.get("id", None)
    cred_name = cred.get("name", None)

    existing_cred = None
    if credential_id is not None:
        cred_box = client.privileged_remote_access.get_credential(
            credential_id=credential_id
        )
        if cred_box is not None:
            existing_cred = cred_box.to_dict()
    elif cred_name is not None:
        creds = client.privileged_remote_access.list_credentials().to_list()
        for cred_ in creds:
            if cred_.get("name") == cred_name:
                existing_cred = cred_
                break

    desired_cred = normalize_creds(cred)
    current_cred = normalize_creds(existing_cred) if existing_cred else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_cred.items():
        if key not in fields_to_exclude and current_cred.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_cred.get(key)}, Desired: {value}"
            )

    if existing_cred is not None:
        id = existing_cred.get("id")
        existing_cred.update(cred)
        existing_cred["id"] = id

    if state == "present":
        if existing_cred is not None:
            if differences_detected:
                """Update"""
                existing_cred = deleteNone(
                    {
                        "credential_id": existing_cred.get("id"),
                        "name": existing_cred.get("name"),
                        "description": existing_cred.get("description"),
                        "credential_type": existing_cred.get("credential_type"),
                        "passphrase": existing_cred.get("passphrase"),
                        "password": existing_cred.get("password"),
                        "private_key": existing_cred.get("private_key"),
                        "user_domain": existing_cred.get("user_domain"),
                        "username": existing_cred.get("username"),
                    }
                )
                existing_cred = client.privileged_remote_access.update_credential(
                    **existing_cred
                ).to_dict()
                module.exit_json(changed=True, data=existing_cred)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_cred)
        else:
            """Create"""
            cred = deleteNone(
                {
                    "name": cred.get("name"),
                    "description": cred.get("description"),
                    "credential_type": cred.get("credential_type"),
                    "passphrase": cred.get("passphrase"),
                    "password": cred.get("password"),
                    "private_key": cred.get("private_key"),
                    "user_domain": cred.get("user_domain"),
                    "username": cred.get("username"),
                }
            )
            cred = client.privileged_remote_access.add_credential(**cred).to_dict()
            module.exit_json(changed=True, data=cred)
    elif (
        state == "absent"
        and existing_cred is not None
        and existing_cred.get("id") is not None
    ):
        code = client.privileged_remote_access.delete_credential(
            credential_id=existing_cred.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_cred)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        credential_type=dict(
            type="str",
            required=False,
            choices=["USERNAME_PASSWORD", "SSH_KEY", "PASSWORD"],
        ),
        passphrase=dict(type="str", required=False, no_log=True),
        password=dict(type="str", required=False, no_log=True),
        private_key=dict(type="str", required=False, no_log=True),
        user_domain=dict(type="str", required=False),
        username=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
