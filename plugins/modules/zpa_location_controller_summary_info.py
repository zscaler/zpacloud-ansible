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
module: zpa_location_controller_summary_info
short_description: Retrieves Location Controller summary information.
description:
    - This module will allow the retrieval of summary information about Location Controllers.
    - Location Controller Summary provides a simplified view of location ID, name, and enabled status.
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
      - The unique identifier of the location.
    required: false
    type: str
  name:
    description:
      - Name of the location.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get All Location Controller Summaries
  zscaler.zpacloud.zpa_location_controller_summary_info:
    provider: "{{ zpa_cloud }}"
  register: all_locations

- name: Get Location Controller Summary by Name
  zscaler.zpacloud.zpa_location_controller_summary_info:
    provider: "{{ zpa_cloud }}"
    name: "San Jose Location"

- name: Get Location Controller Summary by ID
  zscaler.zpacloud.zpa_location_controller_summary_info:
    provider: "{{ zpa_cloud }}"
    id: "216199618143442000"
"""

RETURN = r"""
locations:
  description: >-
    A list of dictionaries containing summary details about the Location Controllers.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the location.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the location.
      type: str
      sample: "San Jose Location"
    enabled:
      description: Indicates whether the location is enabled.
      type: bool
      sample: true
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

    location_id = module.params.get("id")
    location_name = module.params.get("name")

    # Fetch all location summaries
    locations, err = collect_all_items(
        client.location_controller.get_location_summary, {}
    )
    if err:
        module.fail_json(msg=f"Error listing location summaries: {to_native(err)}")

    if not locations:
        module.fail_json(msg="No location summaries found")

    # Convert to list of dicts
    all_locations = []
    for loc in locations:
        loc_dict = loc.as_dict() if hasattr(loc, "as_dict") else loc
        all_locations.append(
            {
                "id": loc_dict.get("id", ""),
                "name": loc_dict.get("name", ""),
                "enabled": loc_dict.get("enabled", False),
            }
        )

    # If ID is specified, filter by ID
    if location_id:
        matched = None
        for loc in all_locations:
            if loc.get("id") == location_id:
                matched = loc
                break
        if not matched:
            module.fail_json(msg=f"Location with ID '{location_id}' not found")
        module.exit_json(changed=False, locations=[matched])

    # If name is specified, filter by name
    if location_name:
        matched = None
        for loc in all_locations:
            if loc.get("name") == location_name:
                matched = loc
                break
        if not matched:
            available = [loc.get("name") for loc in all_locations]
            module.fail_json(
                msg=f"Location with name '{location_name}' not found. Available: {available}"
            )
        module.exit_json(changed=False, locations=[matched])

    # Return all locations if no filter specified
    module.exit_json(changed=False, locations=all_locations)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["id", "name"]],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
