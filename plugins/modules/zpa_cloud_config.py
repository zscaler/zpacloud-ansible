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
module: zpa_cloud_config
short_description: Manages ZIA Cloud Config in ZPA.
description:
    - This module will create or update ZIA Cloud Config.
    - ZIA Cloud Config is used to integrate ZPA with ZIA (Zscaler Internet Access).
    - Note that this resource cannot be deleted. Setting state to absent will be ignored.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  zia_cloud_domain:
    description:
      - ZIA cloud domain (without .net suffix).
      - The .net suffix will be automatically appended if not provided.
    required: true
    type: str
    choices:
      - zscaler
      - zscloud
      - zscalerone
      - zscalertwo
      - zscalerthree
      - zscalerbeta
      - zscalergov
      - zscalerten
      - zspreview
  zia_username:
    description:
      - The username for ZIA authentication.
    required: true
    type: str
  zia_password:
    description:
      - The password for ZIA authentication.
      - This is a write-only field and is not returned by the API.
    required: true
    type: str
    no_log: true
  zia_sandbox_api_token:
    description:
      - ZIA sandbox API token.
      - This is a write-only field and is not returned by the API.
    required: true
    type: str
    no_log: true
  zia_cloud_service_api_key:
    description:
      - ZIA cloud service API key.
      - This is a write-only field and is not returned by the API.
    required: true
    type: str
    no_log: true
"""

EXAMPLES = """
- name: Create/Update ZIA Cloud Config
  zscaler.zpacloud.zpa_cloud_config:
    provider: "{{ zpa_cloud }}"
    state: present
    zia_cloud_domain: "zscaler"
    zia_username: "admin@example.com"
    zia_password: "{{ zia_password }}"
    zia_sandbox_api_token: "{{ zia_sandbox_token }}"
    zia_cloud_service_api_key: "{{ zia_api_key }}"
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


def normalize_domain(domain):
    """Ensure the domain has the .net suffix."""
    if domain and not domain.endswith(".net"):
        return domain + ".net"
    return domain


def core(module):
    state = module.params.get("state", "present")
    client = ZPAClientHelper(module)

    # Build the config payload
    zia_cloud_domain = module.params.get("zia_cloud_domain")
    zia_username = module.params.get("zia_username")
    zia_password = module.params.get("zia_password")
    zia_sandbox_api_token = module.params.get("zia_sandbox_api_token")
    zia_cloud_service_api_key = module.params.get("zia_cloud_service_api_key")

    # Normalize the domain
    normalized_domain = normalize_domain(zia_cloud_domain)

    # This resource cannot be deleted, so state=absent is effectively a no-op
    if state == "absent":
        module.exit_json(
            changed=False,
            msg="ZIA Cloud Config cannot be deleted. Use state=present to update.",
        )

    # Get current config
    current_config = None
    try:
        configs, _, err = client.zia_customer_config.get_zia_cloud_service_config()
        if not err and configs and len(configs) > 0:
            current_config = configs[0]
    except Exception:
        pass

    # Check if update is needed
    needs_update = True
    if current_config:
        current_dict = current_config.as_dict() if hasattr(current_config, "as_dict") else current_config
        current_domain = current_dict.get("zia_cloud_domain", "")
        current_username = current_dict.get("zia_username", "")

        # Check if the non-sensitive fields match
        if current_domain == normalized_domain and current_username == zia_username:
            # For sensitive fields, we always update since we can't read them back
            # But if the user provides the same non-sensitive values, we still need to update
            # because the API might have different credentials stored
            needs_update = True

    if module.check_mode:
        module.exit_json(changed=needs_update)

    # Create or update the config
    config_payload = {
        "zia_cloud_domain": normalized_domain,
        "zia_username": zia_username,
        "zia_password": zia_password,
        "zia_sandbox_api_token": zia_sandbox_api_token,
        "zia_cloud_service_api_key": zia_cloud_service_api_key,
    }

    result, _, err = client.zia_customer_config.add_zia_cloud_service_config(**config_payload)
    if err:
        module.fail_json(msg=f"Error configuring ZIA cloud config: {to_native(err)}")

    # Fetch the updated config to return (API doesn't return sensitive fields)
    configs, _, err = client.zia_customer_config.get_zia_cloud_service_config()
    if err:
        module.fail_json(msg=f"Error retrieving updated ZIA cloud config: {to_native(err)}")

    if configs and len(configs) > 0:
        config = configs[0]
        config_dict = config.as_dict() if hasattr(config, "as_dict") else config
        result_config = {
            "zia_cloud_domain": config_dict.get("zia_cloud_domain", ""),
            "zia_username": config_dict.get("zia_username", ""),
        }
    else:
        result_config = {
            "zia_cloud_domain": normalized_domain,
            "zia_username": zia_username,
        }

    module.exit_json(changed=True, config=result_config)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        zia_cloud_domain=dict(
            type="str",
            required=True,
            choices=[
                "zscaler",
                "zscloud",
                "zscalerone",
                "zscalertwo",
                "zscalerthree",
                "zscalerbeta",
                "zscalergov",
                "zscalerten",
                "zspreview",
            ],
        ),
        zia_username=dict(type="str", required=True),
        zia_password=dict(type="str", required=True, no_log=True),
        zia_sandbox_api_token=dict(type="str", required=True, no_log=True),
        zia_cloud_service_api_key=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

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

