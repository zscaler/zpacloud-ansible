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
module: zpa_cloud_browser_isolation_certificate
short_description: Create a CBI Certificate
description:
    - This module will create/update/delete a CBI Certificate resource.
author:
  - William Guilherme (@willguibr)
version_added: "2.0.0"
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
    description: "The unique identifier of the CBI Certificate"
    type: str
    required: false
  name:
    description: The name of the CBI certificate.
    type: str
    required: true
  pem:
    description: The certificate in PEM format.
    type: str
    required: true
"""

EXAMPLES = """
- name: Create/Update/Delete a CBI Certificate
  zscaler.zpacloud.zpa_cloud_browser_isolation_certificate:
    provider: "{{ zpa_cloud }}"
    name: cbi_profile01.acme.com
    pem: "{{ lookup('file', 'server1.pem') }}"
"""

RETURN = """
# The newly created CBI Certificate resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import deleteNone
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_certificate(cbi_banner):
    """
    Remove computed attributes from a cbi certificate dict to make comparison easier.
    """
    normalized = cbi_banner.copy() if cbi_banner else {}
    computed_values = ["id", "is_default", "private_key"]
    for attr in computed_values:
        normalized.pop(attr, None)
    return normalized


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect parameters
    params = [
        "id",
        "name",
        "pem",
    ]
    certificate = {param: module.params.get(param) for param in params}
    certificate_id = certificate.get("id")
    certificate_name = certificate.get("name")

    # Step 1: Fetch existing certificate if possible
    existing_certificate = None
    if certificate_id:
        result, _unused, error = client.cbi_certificate.get_cbi_certificate(
            certificate_id
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving cbi certificate by ID {certificate_id}: {to_native(error)}"
            )
        if result:
            existing_certificate = result.as_dict()

    elif certificate_name:
        certificate_list, _unused, error = (
            client.cbi_certificate.list_cbi_certificates()
        )
        if error:
            module.fail_json(msg=f"Error listing CBI certificates: {to_native(error)}")
        for item in certificate_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == certificate_name:
                existing_certificate = item_dict
                break

    # Step 2: Normalize and compare
    desired_certificate = normalize_certificate(certificate)
    current_certificate = (
        normalize_certificate(existing_certificate) if existing_certificate else {}
    )

    fields_to_ignore = ["id"]
    drift = False

    for k in desired_certificate:
        if k in fields_to_ignore:
            continue
        if desired_certificate.get(k) != current_certificate.get(k):
            module.warn(
                f"[DRIFT] Key='{k}' => Desired={desired_certificate.get(k)!r}, Actual={current_certificate.get(k)!r}"
            )
            drift = True

    drift = any(
        desired_certificate.get(k) != current_certificate.get(k)
        for k in desired_certificate
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_certificate))
            or (state == "absent" and existing_certificate)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_certificate:
            if drift:
                update_banner = deleteNone(
                    {
                        "certificate_id": existing_certificate.get("id"),
                        "name": desired_certificate.get("name"),
                        "pem": desired_certificate.get("pem"),
                    }
                )
                updated, _unused, error = client.cbi_certificate.update_cbi_certificate(
                    certificate_id=update_banner.pop("certificate_id"), **update_banner
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating CBI Certificate: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_certificate)
        else:
            create_banner = deleteNone(
                {
                    "name": desired_certificate.get("name"),
                    "pem": desired_certificate.get("pem"),
                }
            )
            created, _unused, error = client.cbi_certificate.add_cbi_certificate(
                **create_banner
            )
            if error:
                module.fail_json(
                    msg=f"Error creating CBI Certificate: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_certificate and existing_certificate.get("id"):
        _unused, _unused, error = client.cbi_certificate.delete_cbi_certificate(
            certificate_id=existing_certificate.get("id"),
        )
        if error:
            module.fail_json(msg=f"Error deleting CBI Certificate: {to_native(error)}")
        module.exit_json(changed=True, data=existing_certificate)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        pem=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
