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
module: zpa_ba_certificate_facts
short_description: Retrieves browser access certificate information.
description:
    - This module will allow the retrieval of information about a browser access certificate.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
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
  zscaler.zpacloud.zpa_ba_certificate_facts:
    provider: "{{ zpa_cloud }}"

- name: Gather Details of a Specific Browser Certificates by Name
  zscaler.zpacloud.zpa_ba_certificate_facts:
    provider: "{{ zpa_cloud }}"
    name: crm.acme.com

- name: Gather Details of a Specific Browser Certificates by ID
  zscaler.zpacloud.zpa_ba_certificate_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = """
# Returns information on a specified Browser Access certificate.
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
        certificates = client.certificates.list_issued_certificates().to_list()
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
