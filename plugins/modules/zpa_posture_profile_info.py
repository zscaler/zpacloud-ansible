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
module: zpa_posture_profile_info
short_description: Retrieves details of a posture profile resource.
description:
  - This module will allow the retrieval of information about a posture profile resource.
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
  zscaler.zpacloud.zpa_posture_profile_info:

- name: Get Details of a Specific Posture Profile by ID
  zscaler.zpacloud.zpa_posture_profile_info:
    id: "216196257331282583"
- name: Get Details of a Specific Posture Profile by Name
  zscaler.zpacloud.zpa_posture_profile_info:
    name: CrowdStrike_ZPA_Pre-ZTA
"""

RETURN = """
# Returns information on a specified posture profile.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
import re


def remove_cloud_suffix(s: str) -> str:
    reg = re.compile(r"(.*)[\s]+\([a-zA-Z0-9\-_\.]*\)[\s]*$")
    res = reg.sub(r"\1", s)
    return res.strip()


def core(module: AnsibleModule):
    profile_id = module.params.get("id", None)
    profile_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    profiles = []
    if profile_id is not None:
        profile_box = client.posture_profiles.get_profile(profile_id=profile_id)
        if profile_box is None:
            module.fail_json(
                msg="Failed to retrieve Posture Profile ID: '%s'" % (profile_id)
            )
        profiles = [profile_box.to_dict()]
    else:
        profiles = client.posture_profiles.list_profiles().to_list()
        if profile_name is not None:
            profile_found = False
            for profile in profiles:
                if remove_cloud_suffix(profile.get("name")) == remove_cloud_suffix(
                    profile_name
                ):
                    profile_found = True
                    profiles = [profile]
            if not profile_found:
                module.fail_json(
                    msg="Failed to retrieve Posture Profile  Name: '%s'"
                    % (profile_name)
                )
    module.exit_json(changed=False, data=profiles)


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
