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

DOCUMENTATION = r"""
---
module: zpa_cloud_browser_isolation_banner_info
short_description: Retrieve CBI Banners.
description:
    - This module will allow the retrieval of CBI Banners.
author:
  - William Guilherme (@willguibr)
version_added: "2.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
     - Name of the server group.
    required: false
    type: str
  id:
    description:
     - ID of the server group.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Gather Information Details of All CBI Banners
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Information Details of an CBI Banner by Name
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"
    name: Example CBI Banner

- name: Gather Information Details of an CBI Banner  by ID
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner_info:
    provider: "{{ zpa_cloud }}"
    id: "70132442-25f8-44eb-a5bb-caeaac67c201"
"""

RETURN = r"""
banners:
  description: >
    A list of dictionaries containing details about the specified CBI Banners.
    If a banner is found by ID or name, only that banner will be returned.
    If no filters are provided, all available CBI banners will be returned.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the CBI Banner.
      type: str
      sample: "70132442-25f8-44eb-a5bb-caeaac67c201"
    name:
      description: The name of the CBI Banner.
      type: str
      sample: "Example CBI Banner"
    banner:
      description: Indicates if the banner is active.
      type: bool
      sample: true
    is_default:
      description: Indicates if this is the default system banner.
      type: bool
      sample: false
    logo:
      description: Base64-encoded logo image displayed in the banner.
      type: str
      sample: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAYQAAABQCAMAAAAuu/JsAAAD..."
    notification_title:
      description: Title of the notification shown in the banner.
      type: str
      sample: "Heads up, you've been redirected to Browser Isolation!"
    notification_text:
      description: Detailed message shown in the banner.
      type: str
      sample: "The website you were trying to access is now rendered in a fully isolated environment to protect you from malicious content."
    primary_color:
      description: Primary background color of the banner.
      type: str
      sample: "#0076BE"
    text_color:
      description: Text color used in the banner.
      type: str
      sample: "#FFFFFF"
    persist:
      description: Whether the banner should persist across sessions.
      type: bool
      sample: false

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    banner_id = module.params.get("id")
    banner_name = module.params.get("name")

    results = []

    try:
        # Case 1: Search by ID
        if banner_id:
            banner, _unused, error = client.cbi_banner.get_cbi_banner(banner_id)
            if error:
                module.fail_json(
                    msg=f"Error retrieving banner by ID {banner_id}: {to_native(error)}"
                )
            if banner:
                results = [banner.as_dict()]

        # Case 2: Search by name
        elif banner_name:
            banner_list, _unused, error = client.cbi_banner.list_cbi_banners()
            if error:
                module.fail_json(msg=f"Error listing CBI banners: {to_native(error)}")
            for item in banner_list or []:
                item_dict = item.as_dict()
                if item_dict.get("name") == banner_name:
                    results = [item_dict]
                    break

        # Case 3: Return all
        else:
            banner_list, _unused, error = client.cbi_banner.list_cbi_banners()
            if error:
                module.fail_json(msg=f"Error listing CBI banners: {to_native(error)}")
            results = [item.as_dict() for item in banner_list or []]

        module.exit_json(changed=False, banners=results)

    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
