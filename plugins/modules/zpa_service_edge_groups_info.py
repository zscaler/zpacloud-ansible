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
module: zpa_service_edge_groups_info
short_description: Retrieves information about a Service Edge Group.
description:
    - This module will allow the retrieval of information about a Service Edge Group resource.
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
      - Name of the Service Edge Group.
    required: false
    type: str
  id:
    description:
      - ID of the Service Edge Group.
    required: false
    type: str
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
"""

EXAMPLES = """
- name: Get information about all Service Edge Groups
  zscaler.zpacloud.zpa_service_edge_groups_info:
    provider: "{{ zpa_cloud }}"

- name: Get information about Service Edge Connector Group by ID
  zscaler.zpacloud.zpa_service_edge_groups_info:
    provider: "{{ zpa_cloud }}"
    id: "198288282"

- name: Get information about Service Edge Connector Group by Name
  zscaler.zpacloud.zpa_service_edge_groups_info:
    provider: "{{ zpa_cloud }}"
    name: "Example"
"""

RETURN = r"""
groups:
  description: >-
    A list of dictionaries containing details about the Service Edge Groups.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Service Edge Group.
      type: str
      sample: "216199618143442002"
    name:
      description: The name of the Service Edge Group.
      type: str
      sample: "Example200"
    city_country:
      description: The city and country where the Service Edge Group is located.
      type: str
      sample: "San Jose, US"
    country_code:
      description: The country code of the Service Edge Group location.
      type: str
      sample: "US"
    creation_time:
      description: The timestamp when the Service Edge Group was created.
      type: str
      sample: "1724112382"
    enabled:
      description: Indicates whether the Service Edge Group is enabled.
      type: bool
      sample: true
    grace_distance_enabled:
      description: Indicates if grace distance is enabled for the Service Edge Group.
      type: bool
      sample: false
    grace_distance_value_unit:
      description: The unit of measure for the grace distance value.
      type: str
      sample: "MILES"
    is_public:
      description: Indicates whether the Service Edge Group is public.
      type: str
      sample: "FALSE"
    latitude:
      description: The latitude of the Service Edge Group's location.
      type: str
      sample: "37.33874"
    location:
      description: The specific location details of the Service Edge Group.
      type: str
      sample: "San Jose, CA, USA"
    longitude:
      description: The longitude of the Service Edge Group's location.
      type: str
      sample: "-121.8852525"
    microtenant_name:
      description: The name of the microtenant associated with the Service Edge Group.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the Service Edge Group.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the Service Edge Group was last modified.
      type: str
      sample: "1724112382"
    override_version_profile:
      description: Indicates if the version profile override is enabled.
      type: bool
      sample: false
    upgrade_day:
      description: The day of the week scheduled for upgrades.
      type: str
      sample: "MONDAY"
    upgrade_priority:
      description: The priority assigned for upgrades.
      type: str
      sample: "WEEK"
    upgrade_time_in_secs:
      description: The time in seconds when the upgrade is scheduled.
      type: str
      sample: "25200"
    use_in_dr_mode:
      description: Indicates if the Service Edge Group is used in disaster recovery mode.
      type: bool
      sample: false
    version_profile_id:
      description: The version profile ID associated with the Service Edge Group.
      type: str
      sample: "0"
    version_profile_name:
      description: The version profile name associated with the Service Edge Group.
      type: str
      sample: "Default"
    version_profile_visibility_scope:
      description: The scope of visibility for the version profile.
      type: str
      sample: "ALL"
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

    group_id = module.params.get("id")
    group_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    if group_id:
        result, _unused, error = client.service_edge_group.get_service_edge_group(
            group_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve Service Edge Group ID '{group_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, groups=[result.as_dict()])

    # If no ID, we fetch all
    group_list, err = collect_all_items(
        client.service_edge_group.list_service_edge_groups, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving Service Edge Groups: {to_native(err)}")

    result_list = [g.as_dict() for g in group_list]

    if group_name:
        matched = next((g for g in result_list if g.get("name") == group_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"Service Edge Group '{group_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, groups=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
