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
module: zpa_app_protection_predefined_control_info
short_description: Retrieves App Protection Predefined Control information.
description:
  - This module will allow the retrieval of information about an App Protection Predefined Control from the ZPA Cloud.
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
  id:
    description:
      - The unique identifier of the predefined control.
    required: false
    type: str
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
    default: OWASP_CRS/3.3.0
"""

EXAMPLES = """
- name: Get Details of All App Protection Predefined Control
  zscaler.zpacloud.zpa_app_protection_predefined_control_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific App Predefined Control by Name
  zscaler.zpacloud.zpa_app_protection_predefined_control_info:
    provider: "{{ zpa_cloud }}"
    name: Example

- name: Get Details of a specific App Predefined Control by ID
  zscaler.zpacloud.zpa_app_protection_predefined_control_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = r"""
controls:
  description: >-
    A list of dictionaries containing details about the App Protection Predefined Controls.
  returned: always
  type: list
  elements: dict
  contains:
    control_group:
      description: The group to which the control belongs (e.g., Protocol Issues).
      type: str
      sample: "Protocol Issues"
    default_group:
      description: Indicates if this is a default control group.
      type: bool
      sample: false
    predefined_inspection_controls:
      description: A list of predefined inspection controls under the control group.
      type: list
      elements: dict
      contains:
        id:
          description: The unique identifier of the predefined control.
          type: str
          sample: "72057594037930388"
        name:
          description: The name of the predefined control.
          type: str
          sample: "Failed to parse request body"
        control_number:
          description: The control number.
          type: str
          sample: "200002"
        control_type:
          description: The type of control (e.g., PREDEFINED).
          type: str
          sample: "PREDEFINED"
        description:
          description: A brief description of the predefined control.
          type: str
          sample: "Failed to parse request body"
        severity:
          description: The severity level of the control.
          type: str
          sample: "CRITICAL"
        protocol_type:
          description: The protocol type associated with the control.
          type: str
          sample: "HTTP"
        default_action:
          description: The default action for this control.
          type: str
          sample: "BLOCK"
        paranoia_level:
          description: The paranoia level associated with the control.
          type: str
          sample: "1"
        version:
          description: The version of the control.
          type: str
          sample: "OWASP_CRS/3.3.0"
        creation_time:
          description: The timestamp when the control was created.
          type: str
          sample: "1631459708"
        modified_time:
          description: The timestamp when the control was last modified.
          type: str
          sample: "1631459708"
        associated_inspection_profile_names:
          description: A list of associated inspection profile names that use this control.
          type: list
          elements: dict
          contains:
            id:
              description: The unique identifier of the inspection profile.
              type: str
              sample: "216199618143270390"
            name:
              description: The name of the inspection profile.
              type: str
              sample: "BD_SA_Profile1"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    control_id = module.params.get("id")
    control_name = module.params.get("name")
    version = module.params.get("version")
    client = ZPAClientHelper(module)
    controls = []

    if control_id:
        control_box = client.inspection.get_predef_control(control_id=control_id)
        if not control_box:
            module.fail_json(
                msg="Failed to retrieve App Protection Predefined Control ID: '{control_id}'"
            )
        controls = [control_box.to_dict()]

    elif control_name:
        try:
            control = client.inspection.get_predef_control_by_name(
                control_name, version
            )
            controls = [control.to_dict()]
        except ValueError as ve:
            module.fail_json(msg=to_native(ve))

    else:
        controls = client.inspection.list_predef_controls(version=version).to_list()

    module.exit_json(changed=False, controls=controls)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        version=dict(type="str", default="OWASP_CRS/3.3.0"),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
