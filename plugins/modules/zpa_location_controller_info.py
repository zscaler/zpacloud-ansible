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
module: zpa_location_controller_info
short_description: Retrieves information about a Location Controller.
description:
    - This module will allow the retrieval of information about a Location Controller.
    - Location Controllers are associated with extranet resources and represent physical locations.
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
     - Name of the location.
    required: true
    type: str
  zia_er_name:
    description:
     - Name of the extranet resource partner.
    required: true
    type: str
"""

EXAMPLES = """
- name: Get Details of a Location Controller by Name
  zscaler.zpacloud.zpa_location_controller_info:
    provider: "{{ zpa_cloud }}"
    name: "San Jose Location"
    zia_er_name: "Partner_ER"
"""

RETURN = r"""
locations:
  description: >-
    A list of dictionaries containing details about the Location Controllers.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Location Controller.
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

    location_name = module.params.get("name")
    zia_er_name = module.params.get("zia_er_name")

    # Validate required parameters
    if not location_name or not zia_er_name:
        module.fail_json(msg="Both 'name' and 'zia_er_name' are required")

    # Step 1: Get the extranet resource to obtain zpn_er_id
    query_params = {}
    er_list, err = collect_all_items(
        client.extranet_resource.list_extranet_resources, query_params
    )
    if err:
        module.fail_json(msg=f"Error listing extranet resources: {to_native(err)}")

    # Find the extranet resource by name
    extranet_resource = None
    for er in er_list:
        er_dict = er.as_dict()
        if er_dict.get("name") == zia_er_name:
            extranet_resource = er_dict
            break

    if not extranet_resource:
        module.fail_json(
            msg=f"Extranet resource '{zia_er_name}' not found"
        )

    zpn_er_id = extranet_resource.get("id")

    # Step 2: Get locations using zpn_er_id
    locations, _unused, error = client.location_controller.get_location_extranet_resource(
        zpn_er_id, query_params
    )
    if error:
        module.fail_json(
            msg=f"Error fetching locations for extranet resource '{zia_er_name}': {to_native(error)}"
        )

    if not locations:
        module.fail_json(
            msg=f"No locations found for extranet resource '{zia_er_name}'"
        )

    # Step 3: Search for the specific location by name
    result_list = [loc.as_dict() for loc in locations]
    matched = next((loc for loc in result_list if loc.get("name") == location_name), None)

    if not matched:
        available = [loc.get("name") for loc in result_list]
        module.fail_json(
            msg=f"Location '{location_name}' not found for extranet resource '{zia_er_name}'. Available: {available}"
        )

    module.exit_json(changed=False, locations=[matched])


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        zia_er_name=dict(type="str", required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()

