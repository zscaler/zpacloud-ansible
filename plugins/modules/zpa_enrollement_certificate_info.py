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
module: zpa_enrollement_certificate_info
short_description: Retrieves enrollment certificate information.
description:
  - This module will allow the retrieval of information about a Enrollment Certificate detail from the ZPA Cloud.
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
- name: Gather Information Details of All Enrollment Certificates
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"

- name: Gather Information Details of the Root Enrollment Certificates by Name
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"
    name: "Root"

- name: Gather Information Details of the Client Enrollment Certificates by Name
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"
    name: "Client"

- name: Gather Information Details of the Connector Enrollment Certificates by Name
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"
    name: "Connector"

- name: Gather Information Details of the Service Edge Enrollment Certificates by Name
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"
    name: "Service Edge"

- name: Gather Information Details of the Isolation Client Enrollment Certificates by Name
  zscaler.zpacloud.zpa_enrollment_cert_facts:
    provider: "{{ zpa_cloud }}"
    name: "Isolation Client"
"""

RETURN = r"""
# ANY INFORMATION IN THIS DOCUMENT IS FOR EXAMPLE PURPOSES ONLY AND NOT USED IN PRODUCTION
certificates:
  description: >-
    Details of the Enrollment Certificates.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Enrollment Certificate.
      type: str
      returned: always
      sample: "16560"
    name:
      description: The name of the Enrollment Certificate.
      type: str
      returned: always
      sample: "Connector"
    description:
      description: The description of the Enrollment Certificate.
      type: str
      returned: always
      sample: "Connector Enrollment Certificate"
    c_name:
      description: The common name (CN) of the Enrollment Certificate.
      type: str
      returned: always
      sample: "********.zpa-customer.com/Connector"
    certificate:
      description: The full certificate in PEM format.
      type: str
      returned: always
      sample: |
        -----BEGIN CERTIFICATE-----
        MIIDbjCCAlagAwIBAgIQfayCMxHt3mhQbVAuKHCYPTANBgkqhkiG9w0BAQsFADBe
        ...
        -----END CERTIFICATE-----
    csr:
      description: The Certificate Signing Request (CSR) associated with the Enrollment Certificate in PEM format.
      type: str
      returned: always
      sample: |
        -----BEGIN CERTIFICATE REQUEST-----
        MIIC2jCCAcICAQAwYzEQMA4GA1UEChMHWnNjYWxlcjEXMBUGA1UECxMOUHJpdmF0
        ...
        -----END CERTIFICATE REQUEST-----
    public_key_present:
      description: Indicates whether the private key is present for the Enrollment Certificate.
      type: bool
      returned: always
      sample: true
    serial_no:
      description: The serial number of the Enrollment Certificate.
      type: str
      returned: always
      sample: "167049215292216048285546948781507909693"
    valid_from_in_epoch_sec:
      description: The start of the certificate validity period in epoch seconds.
      type: str
      returned: always
      sample: "1649912246"
    valid_to_in_epoch_sec:
      description: The end of the certificate validity period in epoch seconds.
      type: str
      returned: always
      sample: "2123038646"
    allow_signing:
      description: Indicates whether signing is allowed for this Enrollment Certificate.
      type: bool
      returned: always
      sample: true
    client_cert_type:
      description: The type of client certificate associated with the Enrollment Certificate.
      type: str
      returned: always
      sample: "NONE"
    issued_by:
      description: The issuer of the Enrollment Certificate.
      type: str
      returned: always
      sample: "O=Zscaler,OU=Private Access,CN=********.zpa-customer.com/Root"
    issued_to:
      description: The entity to which the Enrollment Certificate was issued.
      type: str
      returned: always
      sample: "O=Zscaler,OU=Private Access,CN=********.zpa-customer.com/Connector"
    parent_cert_id:
      description: The unique identifier of the parent certificate if this is an intermediate certificate.
      type: str
      returned: always
      sample: "16558"
    parent_cert_name:
      description: The name of the parent certificate.
      type: str
      returned: always
      sample: "Root"
    creation_time:
      description: The time when the Enrollment Certificate was created, in epoch format.
      type: str
      returned: always
      sample: "1649998646"
    modified_time:
      description: The time when the Enrollment Certificate was last modified, in epoch format.
      type: str
      returned: always
      sample: "1693027973"
    modified_by:
      description: The ID of the user who last modified the Enrollment Certificate.
      type: str
      returned: always
      sample: "123456789"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)

    certificate_id = module.params.get("id")
    certificate_name = module.params.get("name")

    query_params = {}

    if certificate_id:
        result, _unused, error = client.enrollment_certificates.get_enrolment(
            certificate_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Enrollment Certificate ID '{certificate_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, certificates=[result.as_dict()])

    # If no ID, we fetch all
    cert_list, err = collect_all_items(
        client.enrollment_certificates.list_enrolment, query_params
    )
    if err:
        module.fail_json(
            msg=f"Error retrieving Enrollment Certificates: {to_native(err)}"
        )

    result_list = [g.as_dict() for g in cert_list]

    if certificate_name:
        matched = next(
            (g for g in result_list if g.get("name") == certificate_name), None
        )
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Enrollment Certificate '{certificate_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, certificates=result_list)


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
