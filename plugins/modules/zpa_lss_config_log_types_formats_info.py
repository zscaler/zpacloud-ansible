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
module: zpa_lss_config_log_types_formats_info
short_description: Retrieves LSS Log formats Information.
description:
  - This module will allow the retrieval of LSS (Log Streaming Services) Log formats information from the ZPA Cloud.
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
  log_type:
    description:
      - Log type
    required: true
    type: str
    choices:
      - zpn_trans_log
      - zpn_auth_log
      - zpn_ast_auth_log
      - zpn_http_trans_log
      - zpn_audit_log
      - zpn_ast_comprehensive_stats
      - zpn_sys_auth_log
      - zpn_waf_http_exchanges_log
      - zpn_pbroker_comprehensive_stats
"""

EXAMPLES = """
- name: Gather LSS Log types formats
  zscaler.zpacloud.zpa_lss_config_log_types_formats_info:
    provider: "{{ zpa_cloud }}"
    log_type: zpn_trans_log
"""

RETURN = r"""
data:
  description: >-
    A dictionary containing the LSS log format templates in various formats (CSV, JSON, TSV) for the specified log type.
  returned: always
  type: dict
  contains:
    csv:
      description: The log format template in CSV format.
      type: str
      sample: "%s{LogTimestamp:time} User Activity zpa-lss: ,%s{Customer},%s{SessionID},..."
    json:
      description: The log format template in JSON format.
      type: str
      sample: "{\"LogTimestamp\": %j{LogTimestamp:time},\"Customer\": %j{Customer},\"SessionID\": %j{SessionID},..."
    tsv:
      description: The log format template in TSV format.
      type: str
      sample: "%s{LogTimestamp:time} User Activity zpa-lss: \\t%s{Customer}\\t%s{SessionID}\\t%s{ConnectionID},..."
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    log_type = module.params.get("log_type")

    log_format = client.lss.get_all_log_formats(log_type=log_type)

    if log_format is None:
        module.fail_json(
            msg=f"Failed to retrieve LSS log format{' for ' + log_type if log_type else ''}."
        )

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
                "zpn_waf_http_exchanges_log",
                "zpn_pbroker_comprehensive_stats",
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
