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
module: zpa_isolation_profile_info
short_description: Retrieves Isolation Profile information.
description:
  - This module will allow the retrieval of information about an Cloud Browser Isolation Profile from the ZPA Cloud.
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
      - Name of the Cloud Browser Isolation profile.
    required: false
    type: str
  id:
    description:
      - ID of the Cloud Browser Isolation profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All Cloud Browser Isolation profiles
  zscaler.zpacloud.zpa_isolation_profile_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific Cloud Browser Isolation profile by Name
  zscaler.zpacloud.zpa_isolation_profile_facts:
    provider: "{{ zpa_cloud }}"
    name: ZPA_CBI_Profile

- name: Get Details of a specific Cloud Browser Isolation profile by ID
  zscaler.zpacloud.zpa_isolation_profile_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = r"""
profiles:
  description: >-
    Details of the Cloud Browser Isolation Profiles.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Cloud Browser Isolation Profile.
      type: str
      returned: always
      sample: "216199618143212401"
    name:
      description: The name of the Cloud Browser Isolation Profile.
      type: str
      returned: always
      sample: "BD_SA_Profile1"
    description:
      description: The description of the Cloud Browser Isolation Profile.
      type: str
      returned: always
      sample: "BD_SA_Profile1"
    enabled:
      description: Indicates whether the Cloud Browser Isolation Profile is enabled.
      type: bool
      returned: always
      sample: true
    creation_time:
      description: The time when the Cloud Browser Isolation Profile was created, in epoch format.
      type: str
      returned: always
      sample: "1675813407"
    modified_time:
      description: The time when the Cloud Browser Isolation Profile was last modified, in epoch format.
      type: str
      returned: always
      sample: "1683812808"
    modified_by:
      description: The ID of the user who last modified the Cloud Browser Isolation Profile.
      type: str
      returned: always
      sample: "72057594037929825"
    isolation_profile_id:
      description: The unique identifier for the Isolation Profile associated with the Cloud Browser.
      type: str
      returned: always
      sample: "fdeffec0-9f76-4f42-a39b-9233a1cc09c8"
    isolation_tenant_id:
      description: The unique identifier for the tenant associated with the Isolation Profile.
      type: str
      returned: always
      sample: "8ba47504-e249-4f34-a9ca-6a8fd0a3c322"
    isolation_url:
      description: The URL for the Cloud Browser Isolation service.
      type: str
      returned: always
      sample: "https://redirect.isolation.zscaler.com/tenant/d374ac83d089/profile/fdeffec0-9f76-4f42-a39b-9233a1cc09c8/zpa/render"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    profile_id = module.params.get("id", None)
    profile_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    profiles = []
    if profile_id is not None:
        profile_box = client.isolation.get_profile(profile_id=profile_id)
        if profile_box is None:
            module.fail_json(
                msg="Failed to retrieve Cloud Browser Isolation profile ID: '%s'"
                % (profile_id)
            )
        profiles = [profile_box.to_dict()]
    else:
        profiles = client.isolation.list_profiles(pagesize=500).to_list()
        if profile_name is not None:
            profile_found = False
            for profile in profiles:
                if profile.get("name") == profile_name:
                    profile_found = True
                    profiles = [profile]
            if not profile_found:
                module.fail_json(
                    msg="Failed to retrieve Cloud Browser Isolation Name: '%s'"
                    % (profile_name)
                )
    module.exit_json(changed=False, profiles=profiles)


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
