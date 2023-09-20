#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_lss_config_status_codes_info
short_description: Retrieves LSS Status Codes Information.
description:
  - This module will allow the retrieval of LSS (Log Streaming Services) Status Codes information from the ZPA Cloud.
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
"""

EXAMPLES = """
- name: Get Details About All LSS Status Codes
  zscaler.zpacloud.zpa_lss_config_status_codes_info:
  register: lss_status_codes
- debug:
    msg: "{{ lss_status_codes }}"
"""

RETURN = """
data:
    description: LSS Status Codes
    returned: success
    elements: dict
    type: list
    sample:
        [
            {
                "zpn_ast_auth_log":
                    {
                        "ZPN_STATUS_AUTHENTICATED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authenticated",
                                "status": "Success",
                            },
                        "ZPN_STATUS_AUTH_FAILED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authentication failed",
                                "status": "Error",
                            },
                        "ZPN_STATUS_DISCONNECTED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Disconnected",
                                "status": "Success",
                            },
                    },
                "zpn_auth_log":
                    {
                        "ZPN_STATUS_AUTHENTICATED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authenticated",
                                "status": "Success",
                            },
                        "ZPN_STATUS_AUTH_FAILED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authentication failed",
                                "status": "Error",
                            },
                        "ZPN_STATUS_DISCONNECTED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Disconnected",
                                "status": "Success",
                            },
                    },
                "zpn_sys_auth_log":
                    {
                        "ZPN_STATUS_AUTHENTICATED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authenticated",
                                "status": "Success",
                            },
                        "ZPN_STATUS_AUTH_FAILED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Authentication failed",
                                "status": "Error",
                            },
                        "ZPN_STATUS_DISCONNECTED":
                            {
                                "adminAction": "NA",
                                "errorType": "NA",
                                "name": "Disconnected",
                                "status": "Success",
                            },
                    },
                "zpn_trans_log":
                    {
                        "APP_NOT_AVAILABLE":
                            {
                                "adminAction": "NA",
                                "errorType": "InternalError",
                                "name": "CA: Application is not available",
                                "status": "Error",
                            },
                        "AST_MT_SETUP_TIMEOUT_CANNOT_CONN_TO_SERVER":
                            {
                                "adminAction": "Check connectivity to server",
                                "errorType": "ActionableError",
                                "name": "AC: Connection request to server timed out",
                                "status": "Error",
                            },
                        "BRK_MT_AUTH_SAML_CANNOT_ADD_ATTR_TO_HEAP":
                            {
                                "adminAction": "NA",
                                "errorType": "InternalError",
                                "name": "SE: Authentication failed due to insufficient memory",
                                "status": "Error",
                            },
                        "BRK_MT_AUTH_SAML_DECODE_FAIL":
                            {
                                "adminAction": "NA",
                                "errorType": "InternalError",
                                "status": "Error",
                            },
                        "BRK_MT_AUTH_SAML_FAILURE":
                            {
                                "adminAction": "NA",
                                "errorType": "ActionableError",
                                "name": "SE: Authentication unsuccessful",
                                "status": "Error",
                            },
                    },
            },
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
    lss_status_codes = client.lss.get_status_codes(log_type="all")
    module.exit_json(changed=False, data=lss_status_codes)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
