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

DOCUMENTATION = r"""
---
module: zpa_cloud_browser_isolation_certificate_info
short_description: Retrieve CBI Certificates.
description:
    - This module will allow the retrieval of CBI Certificates.
author:
  - William Guilherme (@willguibr)
version_added: "2.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
     - Name of the CBI Certificate.
    required: false
    type: str
  id:
    description:
     - ID of the CBI Certificate.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Gather Information Details of All CBI Certificate
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Information Details of an Certificate by Name
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"
    name: Zscaler Root Certificate

- name: Gather Information Details of an Certificateby ID
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"
    id: "87122222-457f-11ed-b878-0242ac120002"
"""

RETURN = r"""
certificates:
  description: >
    A list of dictionaries containing details about the specified CBI Certificates.
    If a certificate is found by ID or name, only that certificate will be returned.
    If no filters are provided, all available CBI certificates will be returned.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the CBI certificate.
      type: str
      sample: "dfad8a65-1b24-4a97-83e9-a4f1d80139e1"
    name:
      description: The name assigned to the CBI certificate.
      type: str
      sample: "ansible.securitygeek.io"
    is_default:
      description: Indicates whether the certificate is the system default.
      type: bool
      sample: false
    pem:
      description: >
        The full PEM-encoded certificate and private key bundle used by the certificate.
        May include `-----BEGIN PRIVATE KEY-----` and `-----BEGIN CERTIFICATE-----` blocks.
      type: str
      sample: |
        -----BEGIN PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBK...
        -----END PRIVATE KEY-----
        -----BEGIN CERTIFICATE-----
        MIIDlzCCAn+gAwIBAgIUaeR6G0HfbBDLS...
        -----END CERTIFICATE-----
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    certificate_id = module.params.get("id")
    certificate_name = module.params.get("name")

    results = []

    try:
        # Case 1: Retrieve by ID
        if certificate_id:
            cert, _unused, error = client.cbi_certificate.get_cbi_certificate(
                certificate_id
            )
            if error:
                module.fail_json(
                    msg=f"Error retrieving certificate by ID {certificate_id}: {to_native(error)}"
                )
            if cert:
                results = [cert.as_dict()]

        # Case 2: Retrieve by name
        elif certificate_name:
            certs, _unused, error = client.cbi_certificate.list_cbi_certificates()
            if error:
                module.fail_json(msg=f"Error listing certificates: {to_native(error)}")
            for cert in certs or []:
                cert_dict = cert.as_dict()
                if cert_dict.get("name") == certificate_name:
                    results = [cert_dict]
                    break

        # Case 3: Retrieve all
        else:
            certs, _unused, error = client.cbi_certificate.list_cbi_certificates()
            if error:
                module.fail_json(msg=f"Error listing certificates: {to_native(error)}")
            results = [cert.as_dict() for cert in certs or []]

        module.exit_json(changed=False, certificates=results)

    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
