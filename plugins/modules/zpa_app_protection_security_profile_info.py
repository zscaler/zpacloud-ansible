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
module: zpa_app_protection_security_profile_info
short_description: Retrieves App Protection Security Profile information.
description:
  - This module will allow the retrieval of information about an App Protection Profile from the ZPA Cloud.
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
      - Name of the App Protection Security Profile.
    required: false
    type: str
  id:
    description:
      - The unique identifier of the AppProtection profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All App Protection profiles
  zscaler.zpacloud.zpa_app_protection_security_profile_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific App Protection profiles by Name
  zscaler.zpacloud.zpa_app_protection_security_profile_info:
    provider: "{{ zpa_cloud }}"
    name: Example

- name: Get Details of a specific App Protection profiles by ID
  zscaler.zpacloud.zpa_app_protection_security_profile_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = r"""
profiles:
  description: >-
    A list of dictionaries containing details about the App Protection Security Profiles.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the App Protection Security Profile.
      type: str
      sample: "216199618143270085"
    name:
      description: The name of the App Protection Security Profile.
      type: str
      sample: "BD_AppProtection_Profile1"
    description:
      description: A brief description of the App Protection Security Profile.
      type: str
      sample: "BD_AppProtection_Profile1"
    api_profile:
      description: Indicates if the profile is an API profile.
      type: bool
      sample: false
    controls_info:
      description: A list of controls associated with the profile, including type and count.
      type: list
      elements: dict
      contains:
        control_type:
          description: The type of control (e.g., PREDEFINED, CUSTOM).
          type: str
          sample: "PREDEFINED"
        count:
          description: The number of controls of this type.
          type: str
          sample: "207"
    global_control_actions:
      description: A list of global control actions associated with the profile.
      type: list
      elements: str
      sample:
        - "PREDEFINED:NONE"
        - "CUSTOM:NONE"
    creation_time:
      description: The timestamp when the profile was created.
      type: str
      sample: "1699401350"
    modified_time:
      description: The timestamp when the profile was last modified.
      type: str
      sample: "1720243144"
    modified_by:
      description: The ID of the user who last modified the profile.
      type: str
      sample: "216199618143191053"
    incarnation_number:
      description: The incarnation number of the profile, which indicates version or iteration.
      type: str
      sample: "6"
    paranoia_level:
      description: The paranoia level set for the profile, which affects the strictness of security checks.
      type: str
      sample: "1"
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

    query_params = {}

    if profile_id:
        result, _unused, error = client.app_protection.get_profile(
            profile_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve app protection profile ID '{profile_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, profiles=[result.as_dict()])

    # If no ID, we fetch all
    cert_list, err = collect_all_items(
        client.app_protection.list_profiles, query_params
    )
    if err:
        module.fail_json(
            msg=f"Error retrieving app protection profile: {to_native(err)}"
        )

    result_list = [g.as_dict() for g in cert_list]

    if profile_name:
        matched = next((g for g in result_list if g.get("name") == profile_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"app protection profile '{profile_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, profiles=result_list)


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
