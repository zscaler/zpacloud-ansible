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
module: zpa_customer_version_profile_info
short_description: Retrieves visible version profiles.
description:
    - This module will allow the retrieval visible version profiles to be associated with app connector groups.
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
      - The name of the version profile.
    required: false
    type: str
  id:
    description:
      - The unique identifier of the version profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Gather Details of All Visible Version Profiles
  zscaler.zpacloud.zpa_customer_version_profile_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Details of a Specific Visible Version Profiles by Name
  zscaler.zpacloud.zpa_customer_version_profile_info:
    provider: "{{ zpa_cloud }}"
    name: crm.acme.com

- name: Gather Details of a Specific Visible Version Profiles by ID
  zscaler.zpacloud.zpa_customer_version_profile_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = r"""
# ANY INFORMATION IN THIS DOCUMENT IS FOR EXAMPLE PURPOSES ONLY AND NOT USED IN PRODUCTION
profiles:
  description: List of version profiles based on the search criteria or all available profiles if no criteria are provided.
  returned: always
  type: list
  elements: dict
  contains:
    creation_time:
      description: The Unix timestamp when the profile was created.
      type: str
      returned: always
    customer_id:
      description: The unique identifier for the customer to whom the profile belongs.
      type: str
      returned: always
    id:
      description: The unique identifier for the profile.
      type: str
      returned: always
    modified_by:
      description: The unique identifier of the user who last modified the profile.
      type: str
      returned: always
    modified_time:
      description: The Unix timestamp when the profile was last modified.
      type: str
      returned: always
    name:
      description: The name of the profile.
      type: str
      returned: always
    upgrade_priority:
      description: The priority of upgrades for this profile, which can be 'WEEK', 'DAY', or other intervals.
      type: str
      returned: always
    visibility_scope:
      description: The scope of visibility for the profile, such as 'ALL', 'NONE', or other specific scopes.
      type: str
      returned: always
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

    # If profile_id is provided, search by id
    if profile_id is not None:
        profiles = client.connectors.list_version_profiles(
            search=profile_id, pagesize=500
        ).to_list()
        if not profiles:
            module.fail_json(
                msg="Failed to retrieve profile by ID: '%s'" % profile_id
            )
    # If profile_name is provided, search by name
    elif profile_name is not None:
        profiles = client.connectors.list_version_profiles(
            search=profile_name, pagesize=500
        ).to_list()
        if not profiles:
            module.fail_json(
                msg="Failed to retrieve profile by Name: '%s'" % profile_name
            )
    # If neither profile_id nor profile_name is provided, retrieve all profiles
    else:
        profiles = client.connectors.list_version_profiles(pagesize=500).to_list()

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
