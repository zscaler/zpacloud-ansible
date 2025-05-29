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
module: zpa_ba_certificate
short_description: Create certificate in the ZPA Cloud.
description:
    - This module creates/delete a certificate in the ZPA Cloud.
    - The Certificate API do not provide a Update Method.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
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
        description: "The unique identifier of the certificate."
        required: false
        type: str
    name:
        description: The name of the certificate.
        required: true
        type: str
    description:
        description: The description of the certificate
        required: false
        type: str
    cert_blob:
        description:
            - The content of the certificate.
            - The cert_blob field must be in string format and must include the certificate and the private key (in PEM format).
        required: true
        type: str
    microtenant_id:
        description:
        - The unique identifier of the Microtenant for the ZPA tenant
        required: false
        type: str
"""

EXAMPLES = """
- name: Onboard ZPA BA Certificate
  zscaler.zpacloud.zpa_ba_certificate:
    provider: "{{ zpa_cloud }}"
    name: server1.acme.com
    description: server1.acme.com
    cert_blob: "{{ lookup('file', 'server1.pem') }}"
"""

RETURN = """
# The newly created certificate resource record.
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


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Extract and clean parameters
    params = ["id", "name", "description", "cert_blob", "microtenant_id"]
    certificate = {p: module.params.get(p) for p in params}
    cert_id = certificate.get("id")
    cert_name = certificate.get("name")
    microtenant_id = certificate.get("microtenant_id")

    existing_cert = None

    # Step 1: Try to get the certificate by ID
    if cert_id:
        result, _unused, error = client.certificates.get_certificate(
            certificate_id=cert_id,
            query_params={"microtenant_id": microtenant_id} if microtenant_id else {},
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving certificate by ID: {to_native(error)}"
            )
        if result:
            existing_cert = result.as_dict()

    # Step 2: If no ID, try to match by name
    elif cert_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        cert_list, error = collect_all_items(
            client.certificates.list_issued_certificates,
            query_params=query_params,
        )
        if error:
            module.fail_json(msg=f"Error listing certificates: {to_native(error)}")
        for cert in cert_list or []:
            cert_dict = cert.as_dict()
            if cert_dict.get("name") == cert_name:
                existing_cert = cert_dict
                break

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and not existing_cert)
            or (state == "absent" and existing_cert)
        )

    # Step 3: Handle Present
    if state == "present":
        if existing_cert:
            module.exit_json(changed=False, data=existing_cert)
        else:
            payload = deleteNone(
                {
                    "name": certificate.get("name"),
                    "description": certificate.get("description"),
                    "cert_blob": certificate.get("cert_blob"),
                    "microtenant_id": certificate.get("microtenant_id"),
                }
            )
            created, _unused, error = client.certificates.add_certificate(**payload)
            if error:
                module.fail_json(msg=f"Error creating certificate: {to_native(error)}")
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Handle Absent
    if state == "absent" and existing_cert:
        _unused, _unused, error = client.certificates.delete_certificate(
            certificate_id=existing_cert.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting certificate: {to_native(error)}")
        module.exit_json(changed=True, data=existing_cert)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        cert_blob=dict(type="str", required=True),
        microtenant_id=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
