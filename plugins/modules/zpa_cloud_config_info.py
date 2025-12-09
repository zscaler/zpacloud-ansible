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
module: zpa_cloud_config_info
short_description: Retrieves ZIA Cloud Config information.
description:
    - This module will allow the retrieval of ZIA Cloud Config information.
    - ZIA Cloud Config contains the ZIA cloud domain and username configuration.
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

options: {}
"""

EXAMPLES = """
- name: Get ZIA Cloud Config
  zscaler.zpacloud.zpa_cloud_config_info:
    provider: "{{ zpa_cloud }}"
  register: zia_config

- name: Display ZIA Cloud Config
  ansible.builtin.debug:
    msg: "ZIA Cloud Domain: {{ zia_config.config.zia_cloud_domain }}"
"""

RETURN = r"""
config:
  description: >-
    A dictionary containing details about the ZIA Cloud Config.
  returned: always
  type: dict
  contains:
    zia_cloud_domain:
      description: The ZIA cloud domain name.
      type: str
      sample: "zscaler.net"
    zia_username:
      description: The ZIA username.
      type: str
      sample: "admin@example.com"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)

    # Fetch ZIA cloud config
    configs, _unused, err = client.zia_customer_config.get_zia_cloud_service_config()
    if err:
        module.fail_json(msg=f"Error retrieving ZIA cloud config: {to_native(err)}")

    if not configs or len(configs) == 0:
        module.fail_json(msg="No ZIA cloud config found")

    # Get the first config (there should only be one)
    config = configs[0]
    config_dict = config.as_dict() if hasattr(config, "as_dict") else config

    result = {
        "zia_cloud_domain": config_dict.get("zia_cloud_domain", ""),
        "zia_username": config_dict.get("zia_username", ""),
    }

    module.exit_json(changed=False, config=result)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
