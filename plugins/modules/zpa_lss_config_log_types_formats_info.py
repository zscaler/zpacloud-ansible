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
module: zpa_lss_config_log_types_formats_info
short_description: Retrieves LSS Log formats Information.
description:
  - This module will allow the retrieval of LSS (Log Streaming Services) Log formats information from the ZPA Cloud.
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
  log_type:
    description:
      - Log type
    required: true
    choices: ["zpn_trans_log", "zpn_auth_log", "zpn_ast_auth_log", "zpn_http_trans_log", "zpn_audit_log", "zpn_ast_comprehensive_stats", "zpn_sys_auth_log"]
    type: str
"""

EXAMPLES = """
    - name: Gather LSS Log types formats
      zscaler.zpacloud.zpa_lss_config_log_types_formats_info:
        log_type: zpn_trans_log
      register: log_types_formats
    - name: log_types_formats
      debug:
        msg: "{{ log_types_formats }}"
"""

RETURN = """
data:
    description: LSS Log formats
    returned: success
    elements: dict
    type: list
    sample: [
      {
            "csv": "...",
            "json": "...",
            "tsv": "..."
      }
    ]
"""

from re import T
from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    log_type = module.params.get("log_type", None)
    lss_log_formats = client.lss.get_log_formats()
    log_format = lss_log_formats.get(log_type, None)
    module.exit_json(changed=False, data=log_format)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        log_type=dict(
            type="str",
            required=True,
            choices=[
                "zpn_trans_log",
                "zpn_auth_log",
                "zpn_ast_auth_log",
                "zpn_http_trans_log",
                "zpn_audit_log",
                "zpn_ast_comprehensive_stats",
                "zpn_sys_auth_log",
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
