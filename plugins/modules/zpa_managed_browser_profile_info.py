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
module: zpa_managed_browser_profile_info
short_description: Retrieves information about a Managed Browser Profile.
description:
    - This module will allow the retrieval of information about a Managed Browser Profile.
    - Managed Browser Profiles configure browser access policies and posture requirements.
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
  name:
    description:
     - Name of the Managed Browser Profile.
    required: false
    type: str
  id:
    description:
     - ID of the Managed Browser Profile.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Detail Information of All Managed Browser Profiles
  zscaler.zpacloud.zpa_managed_browser_profile_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Managed Browser Profile by Name
  zscaler.zpacloud.zpa_managed_browser_profile_info:
    provider: "{{ zpa_cloud }}"
    name: "Chrome_Profile"

- name: Get Details of a Managed Browser Profile by ID
  zscaler.zpacloud.zpa_managed_browser_profile_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
profiles:
  description: >-
    A list of dictionaries containing details about the Managed Browser Profiles.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Managed Browser Profile.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the Managed Browser Profile.
      type: str
      sample: "Chrome_Profile"
    description:
      description: A brief description of the Managed Browser Profile.
      type: str
      sample: "Chrome browser profile for corporate access"
    browser_type:
      description: The type of browser associated with the profile.
      type: str
      sample: "CHROME"
    customer_id:
      description: The customer ID associated with the profile.
      type: str
      sample: "216199618143191041"
    microtenant_id:
      description: The unique identifier of the microtenant associated with the profile.
      type: str
      sample: "216199618143191041"
    microtenant_name:
      description: The name of the microtenant associated with the profile.
      type: str
      sample: "Default"
    chrome_posture_profile:
      description: Chrome posture profile configuration.
      type: list
      elements: dict
      contains:
        id:
          description: The unique identifier of the Chrome posture profile.
          type: str
          sample: "216199618143442001"
        browser_type:
          description: The browser type for the posture profile.
          type: str
          sample: "CHROME"
        crowd_strike_agent:
          description: Whether CrowdStrike agent is required.
          type: bool
          sample: false
        creation_time:
          description: The timestamp when the posture profile was created.
          type: str
          sample: "1724111641"
        modified_by:
          description: The ID of the user who last modified the posture profile.
          type: str
          sample: "216199618143191041"
        modified_time:
          description: The timestamp when the posture profile was last modified.
          type: str
          sample: "1724111641"
    creation_time:
      description: The timestamp when the profile was created.
      type: str
      sample: "1724111641"
    modified_by:
      description: The ID of the user who last modified the profile.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the profile was last modified.
      type: str
      sample: "1724111641"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)

    profile_id = module.params.get("id")
    profile_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Fetch all managed browser profiles
    profile_list, err = collect_all_items(
        client.managed_browser_profile.list_managed_browser_profiles, query_params
    )
    if err:
        module.fail_json(
            msg=f"Error retrieving Managed Browser Profiles: {to_native(err)}"
        )

    result_list = [p.as_dict() for p in profile_list]

    if profile_id:
        matched = next((p for p in result_list if p.get("id") == profile_id), None)
        if not matched:
            module.fail_json(
                msg=f"Managed Browser Profile ID '{profile_id}' not found."
            )
        result_list = [matched]

    elif profile_name:
        matched = next((p for p in result_list if p.get("name") == profile_name), None)
        if not matched:
            available = [p.get("name") for p in result_list]
            module.fail_json(
                msg=f"Managed Browser Profile '{profile_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, profiles=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["id", "name"]],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
