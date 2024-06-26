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
module: zpa_lss_client_types_facts
short_description: Retrieves Log Streaming Service (LSS) Client Types information from ZPA Cloud.
description:
  - This module queries ZPA Cloud to retrieve information about different Log Streaming Service (LSS) Client Types.
  - The retrieved data can be used in conjunction with the source_log_type parameter for configuring LSS Resources.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  client_type:
    description:
      - Specifies a specific type of LSS client for which information is to be retrieved.
      - If not specified, the module retrieves information for all available LSS client types.
    required: false
    type: str
    choices:
      - zpn_client_type_exporter
      - zpn_client_type_machine_tunnel
      - zpn_client_type_ip_anchoring
      - zpn_client_type_edge_connector
      - zpn_client_type_zapp
      - zpn_client_type_slogger
      - zpn_client_type_zapp_partner
      - zpn_client_type_branch_connector
      - zpn_client_type_zia_inspection
"""

EXAMPLES = """
- name: Retrieve information about all LSS Client Types
  zscaler.zpacloud.zpa_lss_client_types_facts:
    provider: "{{ zpa_cloud }}"

- name: Retrieve information about a specific LSS Client Type (e.g., 'zpn_client_type_exporter')
  zscaler.zpacloud.zpa_lss_client_types_facts:
    provider: "{{ zpa_cloud }}"
    name: zpn_client_type_exporter
"""

RETURN = r"""
# Default return values
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    client_type = module.params.get("client_type")

    # Fetch all client types from the SDK
    all_client_types = client.lss.get_client_types()

    # If a specific client type is provided, filter it manually
    if client_type and client_type in all_client_types:
        filtered_types = {client_type: all_client_types[client_type]}
    else:
        filtered_types = all_client_types

    if hasattr(filtered_types, "to_dict"):
        data = filtered_types.to_dict()
    else:
        data = filtered_types

    module.exit_json(changed=False, data=data)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        client_type=dict(
            type="str",
            required=False,
            choices=[
                "zpn_client_type_exporter",
                "zpn_client_type_machine_tunnel",
                "zpn_client_type_ip_anchoring",
                "zpn_client_type_edge_connector",
                "zpn_client_type_zapp",
                "zpn_client_type_slogger",
                "zpn_client_type_zapp_partner",
                "zpn_client_type_branch_connector",
                "zpn_client_type_zia_inspection",
            ],
        ),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
