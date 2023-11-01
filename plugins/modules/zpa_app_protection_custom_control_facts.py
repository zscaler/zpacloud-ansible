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
module: zpa_app_protection_custom_control_facts
short_description: Retrieves App Protection Custom Control information.
description:
  - This module will allow the retrieval of information about an App Protection Custom Control from the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
options:
  name:
    description:
      - The name of the custom control.
    required: false
    type: str
  id:
    description:
      - The unique identifier of the custom control..
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All App Protection Custom Control
  zscaler.zpacloud.zpa_app_protection_custom_control_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific App Protection Custom Control by Name
  zscaler.zpacloud.zpa_app_protection_custom_control_facts:
    provider: "{{ zpa_cloud }}"
    name: Example

- name: Get Details of a specific App Protection Custom Control by ID
  zscaler.zpacloud.zpa_app_protection_custom_control_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = """
# Returns information on a specified App Protection Custom Control.
"""

from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    control_id = module.params.get("id", None)
    control_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    controls = []
    if control_id is not None:
        control_box = client.inspection.get_custom_control(control_id=control_id)
        if control_box is None:
            module.fail_json(
                msg="Failed to retrieve App Protection Custom Control ID: '%s'"
                % (control_id)
            )
        controls = [control_box.to_dict()]
    else:
        controls = client.inspection.list_custom_controls().to_list()
        if control_name is not None:
            control_found = False
            for control in controls:
                if control.get("name") == control_name:
                    control_found = True
                    controls = [control]
            if not control_found:
                module.fail_json(
                    msg="Failed to retrieve App Protection Custom Control Name: '%s'"
                    % (control_name)
                )
    module.exit_json(changed=False, data=controls)


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
