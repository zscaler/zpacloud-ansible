#!/usr/bin/python
# -*- coding: utf-8 -*-

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
module: zpa_app_protection_all_predefined_controls_facts
short_description: Retrieves App Protection All Predefined Controls information.
description:
  - This module will allow the retrieval of information about an App Protection All Predefined Controls from the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
options:
  name:
    description:
      - Name of the App Protection predefined control.
    required: false
    type: str
  version:
    description:
      - The predefined control version.
    required: false
    type: str
  id:
    description:
      - The unique identifier of the predefined control.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of a Specific App All Predefined Controls
  zscaler.zpacloud.zpa_app_protection_all_predefined_controls_facts:
    provider: "{{ zpa_cloud }}"
    version    : "OWASP_CRS/3.3.0"
    group_name : "Preprocessors"
"""

RETURN = """
# Returns information on a specified App Protection All Predefined Controls.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    group_name = module.params.get("group_name", None)
    version = "OWASP_CRS/3.3.0"  # Implicitly set version
    client = ZPAClientHelper(module)

    if group_name:
        try:
            # Use the new get_predef_control_group_by_name method
            control_group = client.inspection.get_predef_control_group_by_name(
                group_name, version
            )
            module.exit_json(changed=False, data=control_group.to_dict())
        except ValueError as ve:
            module.fail_json(msg=to_native(ve))
    else:
        # Fetch all control groups
        all_control_groups = client.inspection.list_predef_controls(
            version=version
        ).to_list()
        module.exit_json(changed=False, data=all_control_groups)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        group_name=dict(type="str", required=False),
        version=dict(
            type="str", default="OWASP_CRS/3.3.0"
        ),  # This is here for compatibility, but we'll always use the hardcoded version
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
