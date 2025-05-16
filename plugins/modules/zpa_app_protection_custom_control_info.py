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
module: zpa_app_protection_custom_control_info
short_description: Retrieves App Protection Custom Control information.
description:
  - This module will allow the retrieval of information about an App Protection Custom Control from the ZPA Cloud.
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
  zscaler.zpacloud.zpa_app_protection_custom_control_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific App Protection Custom Control by Name
  zscaler.zpacloud.zpa_app_protection_custom_control_info:
    provider: "{{ zpa_cloud }}"
    name: Example

- name: Get Details of a specific App Protection Custom Control by ID
  zscaler.zpacloud.zpa_app_protection_custom_control_info:
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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    control_id = module.params.get("id")
    control_name = module.params.get("name")
    client = ZPAClientHelper(module)

    # Lookup by ID
    if control_id:
        result, _, error = client.app_protection.get_custom_control(
            control_id=control_id
        )
        if error or not result:
            module.fail_json(
                msg=f"Failed to retrieve App Protection Custom Control ID: '{control_id}'"
            )
        module.exit_json(
            changed=False,
            data=[result.as_dict() if hasattr(result, "as_dict") else result],
        )

    # Fetch all controls using pagination
    controls, err = collect_all_items(client.app_protection.list_custom_controls, {})
    if err:
        module.fail_json(msg=f"Error retrieving custom controls: {to_native(err)}")

    # Optional: filter by name
    if control_name:
        match = next(
            (c for c in controls if getattr(c, "name", None) == control_name), None
        )
        if not match:
            available = [getattr(c, "name", "") for c in controls]
            module.fail_json(
                msg=f"Custom control '{control_name}' not found. Available: {available}"
            )
        controls = [match]

    module.exit_json(
        changed=False,
        data=[c.as_dict() if hasattr(c, "as_dict") else c for c in controls],
    )


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
