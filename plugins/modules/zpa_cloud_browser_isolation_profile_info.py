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
module: zpa_cloud_browser_isolation_profile_info
short_description: Retrieve CBI Profile.
description:
    - This module will allow the retrieval of CBI Profile.
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
- name: Gather Information Details of All CBI Profiles
  zscaler.zpacloud.zpa_cloud_browser_isolation_profile_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Information Details of an CBI Profile by Name
  zscaler.zpacloud.zpa_cloud_browser_isolation_profile_info:
    provider: "{{ zpa_cloud }}"
    name: Example CBI Profile

- name: Gather Information Details of an CBI Profile  by ID
  zscaler.zpacloud.zpa_cloud_browser_isolation_profile_info:
    provider: "{{ zpa_cloud }}"
    id: "70132442-25f8-44eb-a5bb-caeaac67c201"
"""

RETURN = r"""
profiles:
  description: >
    A list of CBI Browser Isolation Profiles including their security settings,
    regions, and associated certificate references.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the isolation profile.
      type: str
      sample: "412da7e7-fa92-4fd3-ab74-c8bb6b3eb41c"
    name:
      description: The name of the isolation profile.
      type: str
      sample: "CBI_Profile_Example"
    is_default:
      description: Indicates whether this is the default isolation profile.
      type: bool
      sample: false
    certificate_ids:
      description: A list of associated certificate IDs.
      type: list
      elements: str
      sample: []
    certificates:
      description: A list of certificate objects (if expanded by API).
      type: list
      elements: dict
      sample: []
    region_ids:
      description: A list of region IDs where this profile applies.
      type: list
      elements: str
      sample: []
    regions:
      description: List of region objects assigned to this profile.
      type: list
      elements: dict
      contains:
        id:
          description: The region ID.
          type: str
          sample: "50d8666d-ccfb-4127-a5b4-8f3b1f1c7613"
        name:
          description: The human-readable name of the region.
          type: str
          sample: "Portland Oregon"
    security_controls:
      description: Security control settings applied within the isolation session.
      type: dict
      contains:
        allow_printing:
          description: Whether printing is allowed.
          type: bool
          sample: true
        copy_paste:
          description: Controls copy-paste capability.
          type: str
          sample: "all"
        document_viewer:
          description: Whether the document viewer is enabled.
          type: bool
          sample: true
        flattened_pdf:
          description: Whether PDFs are flattened before rendering.
          type: bool
          sample: false
        local_render:
          description: Whether local rendering is enabled.
          type: bool
          sample: true
        restrict_keystrokes:
          description: Whether keystroke input is restricted.
          type: bool
          sample: false
        upload_download:
          description: Upload/download access policy.
          type: str
          sample: "all"
        camera_and_mic:
          description: Whether camera and microphone are enabled (if present).
          type: bool
          sample: false
        deep_link:
          description: Settings for deep linking specific apps.
          type: dict
          contains:
            enabled:
              description: Whether deep linking is enabled.
              type: bool
              sample: true
            applications:
              description: List of allowed deep link app names.
              type: list
              elements: str
              sample: ["test01"]
        watermark:
          description: Watermark configuration for the session.
          type: dict
          contains:
            enabled:
              description: Whether watermarking is enabled.
              type: bool
              sample: true
            message:
              description: The custom watermark message (if any).
              type: str
              sample: "test"
            show_user_id:
              description: Whether the user ID appears in the watermark.
              type: bool
              sample: true
            show_message:
              description: Whether the message is displayed in the watermark.
              type: bool
              sample: true
            show_timestamp:
              description: Whether to show a timestamp in the watermark.
              type: bool
              sample: true

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
    profile_id = module.params.get("id")
    profile_name = module.params.get("name")

    results = []

    try:
        # Case 1: Search by ID
        if profile_id:
            profile, _unused, error = client.cbi_profile.get_cbi_profile(profile_id)
            if error:
                module.fail_json(
                    msg=f"Error retrieving profile by ID {profile_id}: {to_native(error)}"
                )
            if profile:
                results = [profile.as_dict()]

        # Case 2: Search by name
        elif profile_name:
            profile_list, _unused, error = client.cbi_profile.list_cbi_profiles()
            if error:
                module.fail_json(msg=f"Error listing CBI profiles: {to_native(error)}")
            for item in profile_list or []:
                item_dict = item.as_dict()
                if item_dict.get("name") == profile_name:
                    results = [item_dict]
                    break

        # Case 3: Return all
        else:
            profile_list, _unused, error = client.cbi_profile.list_cbi_profiles()
            if error:
                module.fail_json(msg=f"Error listing CBI profiles: {to_native(error)}")
            results = [item.as_dict() for item in profile_list or []]

        module.exit_json(changed=False, profiles=results)

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
