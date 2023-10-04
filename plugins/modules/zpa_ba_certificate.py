#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
options:
    client_id:
        description: ""
        required: false
        type: str
    client_secret:
        description: ""
        required: false
        type: str
    customer_id:
        description: ""
        required: false
        type: str
    id:
        description: ""
        required: false
        type: str
    name:
        description: The name of the certificate.
        required: True
        type: str
    description:
        description: The description of the certificate
        required: False
        type: str
    cert_blob:
        description:
            - The content of the certificate.
            - The cert_blob field must be in string format and must include the certificate and the private key (in PEM format).
        required: True
        type: str
    state:
        description: "Whether the app should be present or absent."
        type: str
        choices:
            - present
            - absent
        default: present
"""

EXAMPLES = """
- name: Onboard ZPA BA Certificate
    zscaler.zpacloud.zpa_ba_certificate:
    state: present
    name: server1.securitygeek.io
    description: server1.securitygeek.io
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
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    certificate = dict()
    params = [
        "id",
        "name",
        "cert_blob",
    ]
    for param_name in params:
        certificate[param_name] = module.params.get(param_name, None)
    cert_id = certificate.get("id", None)
    cert_name = certificate.get("name", None)
    existing_cert = None

    if cert_id is not None:
        cert_box = client.certificates.get_certificate(cert_id=cert_id)
        if cert_box is not None:
            existing_cert = cert_box.to_dict()
    elif cert_name is not None:
        certificates = client.certificates.list_issued_certificates().to_list()
        for certificate_ in certificates:
            if certificate_.get("name") == cert_name:
                existing_cert = certificate_

    if state == "present":
        if existing_cert is not None:
            module.exit_json(changed=False, msg="Certificate already exists.", data=existing_cert)
        else:
            """Create"""
            certificate = deleteNone(
                dict(
                    name=certificate.get("name"),
                    description=certificate.get("description"),
                    cert_blob=certificate.get("cert_blob"),
                )
            )
            certificate = client.certificates.add_certificate(**certificate).to_dict()
            module.exit_json(changed=True, data=certificate)
    elif state == "absent" and existing_cert is not None:
        code = client.certificates.delete_certificate(cert_id=existing_cert.get("id"))
        if code > 299:
            module.fail_json(changed=False, msg="Failed to delete certificate.", data=None)
        module.exit_json(changed=True, data=existing_cert)
    module.exit_json(changed=False, data={})

def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=True),
        cert_blob=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())

if __name__ == "__main__":
    main()
