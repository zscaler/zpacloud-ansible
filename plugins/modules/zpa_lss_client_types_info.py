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
module: zpa_lss_client_types_info
short_description: Retrieves Log Streaming Service (LSS) Client Types information from ZPA Cloud.
description:
  - This module queries ZPA Cloud to retrieve information about different Log Streaming Service (LSS) Client Types.
  - The retrieved data can be used in conjunction with the source_log_type parameter for configuring LSS Resources.
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
      - client_connector_for_vdi
      - zsdk_pre_login_tunnel
      - zsdk_zero_trust_tunnel
"""

EXAMPLES = """
- name: Retrieve information about all LSS Client Types
  zscaler.zpacloud.zpa_lss_client_types_info:
    provider: "{{ zpa_cloud }}"

- name: Retrieve information about a specific LSS Client Type (e.g., 'zpn_client_type_exporter')
  zscaler.zpacloud.zpa_lss_client_types_info:
    provider: "{{ zpa_cloud }}"
    name: zpn_client_type_exporter
"""

RETURN = r"""
data:
  description: >-
    A dictionary mapping of Log Streaming Service (LSS) Client Types and their respective identifiers.
  returned: always
  type: dict
  contains:
    branch_connector:
      description: Identifier for the Branch Connector client type.
      type: str
      sample: "zpn_client_type_branch_connector"
    client_connector:
      description: Identifier for the Client Connector client type (Zscaler App).
      type: str
      sample: "zpn_client_type_zapp"
    client_connector_partner:
      description: Identifier for the Client Connector Partner client type.
      type: str
      sample: "zpn_client_type_zapp_partner"
    cloud_connector:
      description: Identifier for the Cloud Connector client type (Edge Connector).
      type: str
      sample: "zpn_client_type_edge_connector"
    machine_tunnel:
      description: Identifier for the Machine Tunnel client type.
      type: str
      sample: "zpn_client_type_machine_tunnel"
    web_browser:
      description: Identifier for the Web Browser client type.
      type: str
      sample: "zpn_client_type_exporter"
    zia_inspection:
      description: Identifier for the ZIA Inspection client type.
      type: str
      sample: "zpn_client_type_zia_inspection"
    zia_service_edge:
      description: Identifier for the ZIA Service Edge client type.
      type: str
      sample: "zpn_client_type_ip_anchoring"
    zpa_lss:
      description: Identifier for the ZPA Log Streaming Service (LSS) client type.
      type: str
      sample: "zpn_client_type_slogger"
    zsdk_pre_login_tunnel:
      description: Identifier for the Zscaler SDK Pre-Login Tunnel client type.
      type: str
      sample: "zpn_client_type_simple_zsdk"
    zsdk_zero_trust_tunnel:
      description: Identifier for the Zscaler SDK Zero Trust Tunnel client type.
      type: str
      sample: "zpn_client_type_zsdk"
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

    # Directly pass client_type to the SDK — it handles filtering internally
    result = client.lss.get_client_types(client_type)

    if result is None:
        module.fail_json(msg="Failed to retrieve LSS client types.")

    module.exit_json(changed=False, data=result)


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
                "client_connector_for_vdi",
                "zsdk_pre_login_tunnel",
                "zsdk_zero_trust_tunnel",
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
