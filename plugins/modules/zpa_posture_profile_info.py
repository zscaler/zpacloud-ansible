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
module: zpa_posture_profile_info
short_description: Retrieves details of a posture profile resource.
description:
  - This module will allow the retrieval of information about a posture profile resource.
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
      - Name of the posture profile.
    required: false
    type: str
  id:
    description:
      - ID of the posture profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All Posture Profiles
  zscaler.zpacloud.zpa_posture_profile_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific Posture Profile by ID
  zscaler.zpacloud.zpa_posture_profile_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"

- name: Get Details of a Specific Posture Profile by Name
  zscaler.zpacloud.zpa_posture_profile_facts:
    provider: "{{ zpa_cloud }}"
    name: CrowdStrike_ZPA_Pre-ZTA
"""

RETURN = r"""
profiles:
  description: >-
    Details of the Posture Profiles.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Posture Profile.
      type: str
      returned: always
      sample: "216199618143191254"
    name:
      description: The name of the Posture Profile.
      type: str
      returned: always
      sample: "CrowdStrike_ZPA_Pre-ZTA (zscalertwo.net)"
    creation_time:
      description: The time when the Posture Profile was created, in epoch format.
      type: str
      returned: always
      sample: "1652337552"
    modified_time:
      description: The time when the Posture Profile was last modified, in epoch format.
      type: str
      returned: always
      sample: "1652337552"
    modified_by:
      description: The ID of the user who last modified the Posture Profile.
      type: str
      returned: always
      sample: "72057594037928115"
    apply_to_machine_tunnel_enabled:
      description: Indicates if the posture profile applies to machine tunnels.
      type: bool
      returned: always
      sample: false
    crl_check_enabled:
      description: Indicates if Certificate Revocation List (CRL) check is enabled.
      type: bool
      returned: always
      sample: false
    non_exportable_private_key_enabled:
      description: Indicates if non-exportable private keys are enabled for the profile.
      type: bool
      returned: always
      sample: false
    posture_udid:
      description: The Universal Device Identifier (UDID) associated with the posture profile.
      type: str
      returned: always
      sample: "e2538bb9-af91-49bc-98ea-e90bbe048203"
    zscaler_cloud:
      description: The Zscaler cloud where the posture profile is applied.
      type: str
      returned: always
      sample: "zscalertwo"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
    remove_cloud_suffix,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)

    profile_id = module.params.get("id")
    profile_name = module.params.get("name")

    query_params = {}

    # Get profile by ID
    if profile_id:
        result, _unused, error = client.posture_profiles.get_profile(
            profile_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Posture Profile ID '{profile_id}': {to_native(error)}"
            )
        module.exit_json(
            changed=False,
            data=[result.as_dict() if hasattr(result, "as_dict") else result],
        )

    # Fetch all profiles
    profile_list, err = collect_all_items(
        client.posture_profiles.list_posture_profiles, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving Posture Profiles: {to_native(err)}")

    result_list = [p.as_dict() if hasattr(p, "as_dict") else p for p in profile_list]

    # Match user-friendly profile name without requiring suffix
    if profile_name:
        matched = next(
            (
                p
                for p in result_list
                if remove_cloud_suffix(p.get("name", "")) == profile_name
            ),
            None,
        )
        if not matched:
            available = [remove_cloud_suffix(p.get("name", "")) for p in result_list]
            module.fail_json(
                msg=f"Posture Profile '{profile_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, profiles=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
