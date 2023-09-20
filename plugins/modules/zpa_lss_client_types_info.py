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
module: zpa_lss_client_types_info
short_description: Retrieves LSS Client Types Information.
description:
  - This module will allow the retrieval of LSS (Log Streaming Services) Client Types information from the ZPA Cloud.
  - This can then be associated with the source_log_type parameter when creating an LSS Resource.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
requirements:
  - supported starting from zpa_api >= 2.0
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
  zscaler.zpacloud.zpa_lss_client_types_info:
  register: lss_client_typeps
- debug:
    msg: "{{ lss_client_typeps }}"

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


def core(module: AnsibleModule):
    client_type_id = module.params.get("id", None)
    client_type_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    client_types = []
    if client_type_id is not None:
        lss_box = client.lss.get_client_types(client_type_id=client_type_id)
        if lss_box is None:
            module.fail_json(
                msg="Failed to retrieve Identity Provider ID: '%s'" % (client_type_id)
            )
        client_types = [lss_box.to_dict()]
    else:
        client_types = client.lss.get_client_types().to_list()
        if client_type_name is not None:
            client_type_found = False
            for client_type in client_types:
                if client_type.get("name") == client_type_name:
                    client_type_found = True
                    client_types = [client_type]
            if not client_type_found:
                module.fail_json(
                    msg="Failed to retrieve client type Name: '%s'" % (client_type_name)
                )
    module.exit_json(changed=False, data=client_types)


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
