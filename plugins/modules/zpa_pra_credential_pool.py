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
module: zpa_pra_credential_pool
short_description: Create a PRA Credential Pool.
description:
  - This module will create/update/delete Privileged Remote Access Credential Pool.
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
  credential_ids:
    description: "Privileged Credential IDs"
    type: list
    elements: str
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
    normalize_app,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect parameters
    cred = {
        k: module.params.get(k)
        for k in ["id", "microtenant_id", "name", "credential_type", "credential_ids"]
    }

    pool_id = cred.get("id")
    cred_name = cred.get("name")
    microtenant_id = cred.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    # Step 1: Resolve ID if not provided
    if not pool_id:
        result, error = collect_all_items(
            client.pra_credential_pool.list_credential_pool, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing credential pools: {to_native(error)}")

        for cred_ in result:
            if getattr(cred_, "name", None) == cred_name:
                pool_id = cred_.id
                break

    # Step 2: Fetch full existing object by ID (includes credentials)
    existing_cred = None
    if pool_id:
        result, _unused, error = client.pra_credential_pool.get_credential_pool(
            pool_id, query_params=query_params
        )
        if error:
            module.fail_json(
                msg=f"Error fetching credential pool by ID: {to_native(error)}"
            )
        existing_cred = result.as_dict()

    # Normalize desired and current
    desired_cred = normalize_app(cred)
    current_cred = normalize_app(existing_cred) if existing_cred else {}

    module.warn(f"Normalized Desired: {desired_cred}")
    module.warn(f"Normalized Current: {current_cred}")

    # Normalize credentials block into credential_ids
    if "credentials" in current_cred:
        current_cred["credential_ids"] = sorted(
            str(c["id"]) for c in current_cred["credentials"] if c.get("id")
        )
        current_cred.pop("credentials", None)

    if "credential_ids" in desired_cred:
        desired_cred["credential_ids"] = sorted(
            map(str, desired_cred["credential_ids"])
        )

    # Drift detection
    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_cred.items():
        current_value = current_cred.get(key)

        module.warn(f"Comparing key: {key}, Desired: {value}, Current: {current_value}")

        if key not in fields_to_exclude and current_value != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_value}, Desired: {value}"
            )

    if module.check_mode:
        if state == "present" and (not existing_cred or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_cred:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    # Prepare payloads
    if existing_cred:
        cred["id"] = existing_cred.get("id")  # preserve resolved ID
        existing_cred.update(cred)

    module.warn(f"Final payload being sent to SDK: {cred}")

    if state == "present":
        if existing_cred:
            if differences_detected:
                if existing_cred.get("credential_type") != desired_cred.get(
                    "credential_type"
                ):
                    module.fail_json(
                        msg="Credential type cannot be modified after creation."
                    )

                update_payload = deleteNone(
                    {
                        "pool_id": existing_cred["id"],
                        "microtenant_id": desired_cred.get("microtenant_id"),
                        "name": desired_cred.get("name"),
                        "credential_type": desired_cred.get("credential_type"),
                        "credential_ids": desired_cred.get("credential_ids"),
                    }
                )

                module.warn(f"[UPDATE] Payload: {update_payload}")
                updated_cred, _unused, error = (
                    client.pra_credential_pool.update_credential_pool(
                        pool_id=update_payload.pop("pool_id"), **update_payload
                    )
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating credential: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated_cred.as_dict())
            else:
                module.exit_json(changed=False, data=existing_cred)
        else:
            create_payload = deleteNone(
                {
                    "microtenant_id": desired_cred.get("microtenant_id"),
                    "name": desired_cred.get("name"),
                    "credential_type": desired_cred.get("credential_type"),
                    "credential_ids": desired_cred.get("credential_ids"),
                }
            )

            module.warn(f"[CREATE] Payload: {create_payload}")
            new_cred, _unused, error = client.pra_credential_pool.add_credential_pool(
                **create_payload
            )
            if error:
                module.fail_json(msg=f"Error creating credential: {to_native(error)}")
            module.exit_json(changed=True, data=new_cred.as_dict())

    elif state == "absent" and existing_cred:
        _unused, _unused, error = client.pra_credential_pool.delete_credential_pool(
            pool_id=existing_cred["id"],
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting credential: {to_native(error)}")
        module.exit_json(changed=True, data=existing_cred)

    module.exit_json(changed=False)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()

    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        credential_type=dict(
            type="str",
            required=False,
            choices=["USERNAME_PASSWORD", "SSH_KEY", "PASSWORD"],
        ),
        credential_ids=dict(type="list", elements="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
