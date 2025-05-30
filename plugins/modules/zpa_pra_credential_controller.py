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
notes:
    - Check mode is supported.
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
  update_secret:
    type: bool
    description:
        - Required when attempting to update an existing credential value i.e password
    required: false
    default: false
  user_domain:
    type: str
    description:
        - The domain name associated with the username
        - You can also include the domain name as part of the username
        - The domain name only needs to be specified with logging in to an RDP console that is connected to an Active Directory Domain
    required: false
  user_name:
    type: str
    description:
        - The username for the login you want to use for the privileged credential.
    required: false
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
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

from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_creds(creds):
    return creds or {}


def core(module):
    state = module.params.get("state")
    update_secret = module.params.get("update_secret", False)
    client = ZPAClientHelper(module)

    cred = {
        k: module.params.get(k)
        for k in [
            "id",
            "microtenant_id",
            "name",
            "description",
            "credential_type",
            "passphrase",
            "password",
            "private_key",
            "user_domain",
            "user_name",
        ]
    }

    credential_id = cred.get("id")
    cred_name = cred.get("name")
    microtenant_id = cred.get("microtenant_id")

    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    existing_cred = None
    if credential_id:
        result, _unused, error = client.pra_credential.get_credential(
            credential_id, query_params=query_params
        )
        if error:
            module.fail_json(msg=f"Error fetching credential by ID: {to_native(error)}")
        existing_cred = result.as_dict()
    else:
        result, error = collect_all_items(
            client.pra_credential.list_credentials, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing credentials: {to_native(error)}")
        for cred_ in result:
            if getattr(cred_, "name", None) == cred_name:
                existing_cred = cred_.as_dict()
                break

    desired_cred = normalize_creds(cred)
    current_cred = normalize_creds(existing_cred) if existing_cred else {}

    fields_to_exclude = ["id", "password", "private_key", "passphrase"]
    differences_detected = False
    for key, value in desired_cred.items():
        if key not in fields_to_exclude and current_cred.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_cred.get(key)}, Desired: {value}"
            )

    if module.check_mode:
        if state == "present" and (
            not existing_cred or differences_detected or update_secret
        ):
            module.exit_json(changed=True)
        if state == "absent" and existing_cred:
            module.exit_json(changed=True)
        module.exit_json(changed=False)

    if existing_cred:
        id_ = existing_cred.get("id")
        existing_cred.update(cred)
        existing_cred["id"] = id_

    if state == "present":
        if existing_cred:
            if differences_detected or update_secret:
                if existing_cred.get("credential_type") != desired_cred.get(
                    "credential_type"
                ):
                    module.fail_json(
                        msg="Credential type cannot be modified after creation."
                    )

                update_payload = deleteNone(
                    {
                        "credential_id": existing_cred.get("id"),
                        "microtenant_id": desired_cred.get("microtenant_id"),
                        "name": desired_cred.get("name"),
                        "description": desired_cred.get("description"),
                        "credential_type": desired_cred.get("credential_type"),
                        "passphrase": (
                            desired_cred.get("passphrase") if update_secret else None
                        ),
                        "password": (
                            desired_cred.get("password") if update_secret else None
                        ),
                        "private_key": (
                            desired_cred.get("private_key") if update_secret else None
                        ),
                        "user_domain": desired_cred.get("user_domain"),
                        "user_name": desired_cred.get("user_name"),
                    }
                )

                module.warn(f"[UPDATE] Payload: {update_payload}")
                updated_cred, _unused, error = client.pra_credential.update_credential(
                    credential_id=update_payload.pop("credential_id"), **update_payload
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating credential: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated_cred.as_dict())
            module.exit_json(changed=False, data=existing_cred)
        else:
            create_payload = deleteNone(
                {
                    "microtenant_id": desired_cred.get("microtenant_id"),
                    "name": desired_cred.get("name"),
                    "description": desired_cred.get("description"),
                    "credential_type": desired_cred.get("credential_type"),
                    "passphrase": desired_cred.get("passphrase"),
                    "password": desired_cred.get("password"),
                    "private_key": desired_cred.get("private_key"),
                    "user_domain": desired_cred.get("user_domain"),
                    "user_name": desired_cred.get("user_name"),
                }
            )
            module.warn(f"[CREATE] Payload: {create_payload}")
            new_cred, _unused, error = client.pra_credential.add_credential(
                **create_payload
            )
            if error:
                module.fail_json(msg=f"Error creating credential: {to_native(error)}")
            module.exit_json(changed=True, data=new_cred.as_dict())

    elif state == "absent":
        if existing_cred:
            _unused, _unused, error = client.pra_credential.delete_credential(
                credential_id=existing_cred.get("id"),
                microtenant_id=microtenant_id,
            )
            if error:
                module.fail_json(msg=f"Error deleting credential: {to_native(error)}")
            module.exit_json(changed=True, data=existing_cred)
        module.exit_json(changed=False, data=None)  # Always return data field


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
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
        user_name=dict(type="str", required=False),
        update_secret=dict(type="bool", required=False, default=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
