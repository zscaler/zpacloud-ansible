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
module: zpa_ba_certificate_info
short_description: Retrieves browser access certificate information.
description:
    - This module will allow the retrieval of information about a browser access certificate.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
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
      - Name of the browser certificate.
    required: false
    type: str
  id:
    description:
      - ID of the browser certificate.
    required: false
    type: str
"""

EXAMPLES = """
- name: Gather Details of All Browser Certificates
  zscaler.zpacloud.zpa_ba_certificate_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Details of a Specific Browser Certificates by Name
  zscaler.zpacloud.zpa_ba_certificate_info:
    provider: "{{ zpa_cloud }}"
    name: crm.acme.com

- name: Gather Details of a Specific Browser Certificates by ID
  zscaler.zpacloud.zpa_ba_certificate_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = r"""
# ANY INFORMATION IN THIS DOCUMENT IS FOR EXAMPLE PURPOSES ONLY AND NOT USED IN PRODUCTION
certificates:
  description: >-
    Details of the Browser Access certificates.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Browser Access certificate.
      type: str
      returned: always
      sample: "216199618143247244"
    name:
      description: The name of the Browser Access certificate.
      type: str
      returned: always
      sample: "sales.bd-hashicorp.com"
    description:
      description: The description of the Browser Access certificate.
      type: str
      returned: always
      sample: "sales.bd-hashicorp.com"
    c_name:
      description: The common name (CN) of the Browser Access certificate.
      type: str
      returned: always
      sample: "sales.bd-hashicorp.com"
    certificate:
      description: The full certificate in PEM format.
      type: str
      returned: always
      sample: |
        -----BEGIN CERTIFICATE-----
        MIIF0DCCBLi
        ...
        -----END CERTIFICATE-----
    public_key:
      description: The public key associated with the certificate in PEM format.
      type: str
      returned: always
      sample: |
        -----BEGIN PUBLIC KEY-----
        MIIBIj
        ...
        -----END PUBLIC KEY-----
    san:
      description: A list of Subject Alternative Names (SANs) associated with the certificate.
      type: list
      elements: str
      returned: always
      sample: ["sales.acme.com"]
    issued_by:
      description: The issuer of the certificate.
      type: str
      returned: always
      sample: "CN=acme-VCD126-SRV01-CA,DC=acme,DC=com"
    issued_to:
      description: The entity to which the certificate was issued.
      type: str
      returned: always
      sample: "CN=sales.bd-hashicorp.com,OU=ITDepartment,O=BD-HashiCorp,L=SanJose,ST=CA,C=US"
    serial_no:
      description: The serial number of the certificate.
      type: str
      returned: always
      sample: "735924591743318636302144604206618292491649060"
    valid_from_in_epoch_sec:
      description: The start of the certificate validity period in epoch seconds.
      type: str
      returned: always
      sample: "1693027293"
    valid_to_in_epoch_sec:
      description: The end of the certificate validity period in epoch seconds.
      type: str
      returned: always
      sample: "1756099293"
    creation_time:
      description: The time when the certificate was created, in epoch format.
      type: str
      returned: always
      sample: "1693026759"
    modified_time:
      description: The time when the certificate was last modified, in epoch format.
      type: str
      returned: always
      sample: "1693027973"
    modified_by:
      description: The ID of the user who last modified the certificate.
      type: str
      returned: always
      sample: "216199618143191041"
    microtenant_name:
      description: The name of the microtenant associated with the certificate.
      type: str
      returned: always
      sample: "Default"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    certificate_id = module.params.get("id", None)
    certificate_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    certificates = []
    if certificate_id is not None:
        certificate_box = client.certificates.get_certificate(
            certificate_id=certificate_id
        )
        if certificate_box is None:
            module.fail_json(
                msg="Failed to retrieve Browser Access Certificate ID: '%s'"
                % (certificate_id)
            )
        certificates = [certificate_box.to_dict()]
    else:
        certificates = client.certificates.list_issued_certificates(
            pagesize=500
        ).to_list()
        if certificate_name is not None:
            certificate_found = False
            for certificate in certificates:
                if certificate.get("name") == certificate_name:
                    certificate_found = True
                    certificates = [certificate]
            if not certificate_found:
                module.fail_json(
                    msg="Failed to retrieve Browser Access Certificate Name: '%s'"
                    % (certificate_name)
                )
    module.exit_json(changed=False, certificates=certificates)


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
