#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023, Zscaler, Inc
#
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
module: zpa_lss_client_types_facts
short_description: Retrieves LSS Client Types Information.
description:
  - This module will allow the retrieval of LSS (Log Streaming Services) Client Types information from the ZPA Cloud.
  - This can then be associated with the source_log_type parameter when creating an LSS Resource.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
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
"""

EXAMPLES = """
- name: Get Details About All LSS Client Types
  zscaler.zpacloud.zpa_lss_client_types_facts:
    provider: "{{ zpa_cloud }}"

"""

RETURN = """
data:
    description: Trusted Network information
    returned: success
    elements: dict
    type: list
    sample: [
      {
            "zpn_client_type_edge_connector": "Cloud Connector",
            "zpn_client_type_exporter": "Web Browser",
            "zpn_client_type_ip_anchoring": "ZIA Service Edge",
            "zpn_client_type_machine_tunnel": "Machine Tunnel",
            "zpn_client_type_slogger": "ZPA LSS",
            "zpn_client_type_zapp": "Client Connector"
      }
    ]
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    log_type = module.params.get("log_type", None)
    lss_log_formats = client.lss.get_client_types()
    log_format = lss_log_formats.get(log_type, None)
    module.exit_json(changed=False, data=log_format)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(
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
