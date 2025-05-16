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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    client = ZPAClientHelper(module)
    profile_id = module.params.get("id")
    profile_name = module.params.get("name")

    query_params = {}
    if profile_id:
        query_params["search"] = profile_id
    elif profile_name:
        query_params["search"] = profile_name

    profiles, err = collect_all_items(
        client.customer_version_profile.list_version_profiles, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving version profiles: {to_native(err)}")

    if (profile_id or profile_name) and not profiles:
        module.fail_json(
            msg=f"Version Profile '{profile_id or profile_name}' not found."
        )

    result = [p.as_dict() if hasattr(p, "as_dict") else p for p in profiles]
    module.exit_json(changed=False, data=result)


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
