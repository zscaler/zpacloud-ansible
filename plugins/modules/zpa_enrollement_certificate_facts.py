#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_enrollement_certificate_facts
short_description: Retrieves enrollment certificate information.
description:
  - This module will allow the retrieval of information about a Enrollment Certificate detail from the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider

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

RETURN = """
# Returns information on a specified Enrollment Certificate.
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
        certificate_box = client.certificates.get_enrolment(
            certificate_id=certificate_id
        )
        if certificate_box is None:
            module.fail_json(
                msg="Failed to retrieve Enrollment Certificate ID: '%s'"
                % (certificate_id)
            )
        certificates = [certificate_box.to_dict()]
    else:
        certificates = client.certificates.list_enrolment().to_list()
        if certificate_name is not None:
            certificate_found = False
            for certificate in certificates:
                if certificate.get("name") == certificate_name:
                    certificate_found = True
                    certificates = [certificate]
            if not certificate_found:
                module.fail_json(
                    msg="Failed to retrieve Enrollment Certificate Name: '%s'"
                    % (certificate_name)
                )
    module.exit_json(changed=False, data=certificates)


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
