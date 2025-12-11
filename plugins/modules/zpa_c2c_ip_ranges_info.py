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
module: zpa_c2c_ip_ranges_info
short_description: Retrieves information about C2C IP Ranges.
description:
    - This module will allow the retrieval of information about C2C IP Ranges.
    - C2C IP Ranges define the IP address ranges for Client-to-Client connectivity.
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
     - Name of the C2C IP Range.
    required: false
    type: str
  id:
    description:
     - ID of the C2C IP Range.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Detail Information of All C2C IP Ranges
  zscaler.zpacloud.zpa_c2c_ip_ranges_info:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a C2C IP Range by Name
  zscaler.zpacloud.zpa_c2c_ip_ranges_info:
    provider: "{{ zpa_cloud }}"
    name: "Corporate_Range"

- name: Get Details of a C2C IP Range by ID
  zscaler.zpacloud.zpa_c2c_ip_ranges_info:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
ranges:
  description: >-
    A list of dictionaries containing details about the C2C IP Ranges.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the C2C IP Range.
      type: str
      sample: "216199618143442000"
    name:
      description: The name of the C2C IP Range.
      type: str
      sample: "Corporate_Range"
    description:
      description: A brief description of the C2C IP Range.
      type: str
      sample: "Corporate IP address range"
    enabled:
      description: Indicates whether the C2C IP Range is enabled.
      type: bool
      sample: true
    available_ips:
      description: The number of available IP addresses in the range.
      type: str
      sample: "254"
    country_code:
      description: Country code for the C2C IP Range location.
      type: str
      sample: "US"
    customer_id:
      description: The customer ID associated with the range.
      type: str
      sample: "216199618143191041"
    ip_range_begin:
      description: The beginning IP address of the range.
      type: str
      sample: "192.168.1.1"
    ip_range_end:
      description: The ending IP address of the range.
      type: str
      sample: "192.168.1.254"
    is_deleted:
      description: Whether the C2C IP Range has been deleted.
      type: str
      sample: "false"
    latitude_in_db:
      description: Latitude coordinate stored in the database.
      type: str
      sample: "37.33874"
    location:
      description: Location description for the IP range.
      type: str
      sample: "San Jose, CA, USA"
    location_hint:
      description: A hint about the location of the IP range.
      type: str
      sample: "Created via Ansible"
    longitude_in_db:
      description: Longitude coordinate stored in the database.
      type: str
      sample: "-121.8852525"
    sccm_flag:
      description: Whether the IP range is flagged for SCCM.
      type: bool
      sample: false
    subnet_cidr:
      description: The subnet CIDR notation for the IP range.
      type: str
      sample: "192.168.1.0/24"
    total_ips:
      description: The total number of IP addresses in the range.
      type: str
      sample: "256"
    used_ips:
      description: The number of used IP addresses in the range.
      type: str
      sample: "2"
    creation_time:
      description: The timestamp when the range was created.
      type: str
      sample: "1724111641"
    modified_by:
      description: The ID of the user who last modified the range.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the range was last modified.
      type: str
      sample: "1724111641"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)

    range_id = module.params.get("id")
    range_name = module.params.get("name")

    if range_id:
        result, _unused, error = client.c2c_ip_ranges.get_ip_range(range_id)
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve C2C IP Range ID '{range_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, ranges=[result.as_dict()])

    # If no ID, we fetch all
    range_list, _unused, err = client.c2c_ip_ranges.list_ip_ranges()
    if err:
        module.fail_json(msg=f"Error retrieving C2C IP Ranges: {to_native(err)}")

    result_list = [r.as_dict() for r in range_list]

    if range_name:
        matched = next((r for r in result_list if r.get("name") == range_name), None)
        if not matched:
            available = [r.get("name") for r in result_list]
            module.fail_json(
                msg=f"C2C IP Range '{range_name}' not found. Available: {available}"
            )
        result_list = [matched]

    module.exit_json(changed=False, ranges=result_list)


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
