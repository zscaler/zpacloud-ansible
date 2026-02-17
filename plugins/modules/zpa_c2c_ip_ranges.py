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
module: zpa_c2c_ip_ranges
short_description: Create a C2C IP Range
description:
    - This module will create/update/delete a C2C IP Range resource.
    - C2C IP Ranges define the IP address ranges for Client-to-Client connectivity.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state

options:
  id:
    description: "The unique identifier of the C2C IP Range"
    type: str
    required: false
  name:
    description: "Name of the C2C IP Range"
    type: str
    required: true
  description:
    description: "Description of the C2C IP Range"
    type: str
    required: false
  enabled:
    description: "Whether this C2C IP Range is enabled or not"
    type: bool
    required: false
  ip_range_begin:
    description: "Beginning IP address of the range"
    type: str
    required: false
  ip_range_end:
    description: "Ending IP address of the range"
    type: str
    required: false
  location:
    description: "Location description for the C2C IP Range"
    type: str
    required: false
  location_hint:
    description: "Location hint for the C2C IP Range"
    type: str
    required: false
  sccm_flag:
    description: "SCCM flag for the C2C IP Range"
    type: bool
    required: false
  subnet_cidr:
    description: "Subnet CIDR for the C2C IP Range"
    type: str
    required: false
  country_code:
    description: "Country code for the C2C IP Range location"
    type: str
    required: false
  latitude_in_db:
    description: "Latitude coordinate stored in the database"
    type: str
    required: false
  longitude_in_db:
    description: "Longitude coordinate stored in the database"
    type: str
    required: false
"""

EXAMPLES = """
- name: Create/Update/Delete a C2C IP Range
  zscaler.zpacloud.zpa_c2c_ip_ranges:
    provider: "{{ zpa_cloud }}"
    name: Corporate_Range
    description: Corporate IP address range
    enabled: true
    ip_range_begin: "192.168.1.1"
    ip_range_end: "192.168.1.254"
    location: "San Jose, CA, USA"
    location_hint: "Created via Ansible"
    country_code: "US"
    latitude_in_db: "37.33874"
    longitude_in_db: "-121.8852525"
"""

RETURN = """
# The newly created C2C IP Range resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    normalize_app,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect parameters
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "ip_range_begin",
        "ip_range_end",
        "location",
        "location_hint",
        "sccm_flag",
        "subnet_cidr",
        "country_code",
        "latitude_in_db",
        "longitude_in_db",
    ]
    range_data = {param: module.params.get(param) for param in params}
    range_id = range_data.get("id")
    range_name = range_data.get("name")

    # Step 1: Fetch existing range if possible
    existing_range = None
    if range_id:
        result, _unused, error = client.c2c_ip_ranges.get_ip_range(range_id)
        if error:
            module.fail_json(
                msg=f"Error retrieving C2C IP Range by ID {range_id}: {to_native(error)}"
            )
        if result:
            existing_range = result.as_dict()

    elif range_name:
        range_list, _unused, error = client.c2c_ip_ranges.list_ip_ranges()
        if error:
            module.fail_json(msg=f"Error listing C2C IP Ranges: {to_native(error)}")
        for item in range_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == range_name:
                existing_range = item_dict
                break

    # Step 2: Normalize and compare
    desired_range = normalize_app(range_data)
    current_range = normalize_app(existing_range) if existing_range else {}

    fields_to_ignore = ["id"]

    drift = any(
        desired_range.get(k) != current_range.get(k)
        for k in desired_range
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_range))
            or (state == "absent" and existing_range)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_range:
            if drift:
                update_range = deleteNone(
                    {
                        "name": desired_range.get("name"),
                        "description": desired_range.get("description"),
                        "enabled": desired_range.get("enabled"),
                        "ip_range_begin": desired_range.get("ip_range_begin"),
                        "ip_range_end": desired_range.get("ip_range_end"),
                        "location": desired_range.get("location"),
                        "location_hint": desired_range.get("location_hint"),
                        "sccm_flag": desired_range.get("sccm_flag"),
                        "subnet_cidr": desired_range.get("subnet_cidr"),
                        "country_code": desired_range.get("country_code"),
                        "latitude_in_db": desired_range.get("latitude_in_db"),
                        "longitude_in_db": desired_range.get("longitude_in_db"),
                    }
                )
                updated, _unused, error = client.c2c_ip_ranges.update_ip_range(
                    range_id=existing_range.get("id"), **update_range
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating C2C IP Range: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_range)
        else:
            payload = deleteNone(
                {
                    "name": desired_range.get("name"),
                    "description": desired_range.get("description"),
                    "enabled": desired_range.get("enabled"),
                    "ip_range_begin": desired_range.get("ip_range_begin"),
                    "ip_range_end": desired_range.get("ip_range_end"),
                    "location": desired_range.get("location"),
                    "location_hint": desired_range.get("location_hint"),
                    "sccm_flag": desired_range.get("sccm_flag"),
                    "subnet_cidr": desired_range.get("subnet_cidr"),
                    "country_code": desired_range.get("country_code"),
                    "latitude_in_db": desired_range.get("latitude_in_db"),
                    "longitude_in_db": desired_range.get("longitude_in_db"),
                }
            )
            created, _unused, error = client.c2c_ip_ranges.add_ip_range(**payload)
            if error:
                module.fail_json(msg=f"Error creating C2C IP Range: {to_native(error)}")
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_range and existing_range.get("id"):
        _unused, _unused, error = client.c2c_ip_ranges.delete_ip_range(
            range_id=existing_range.get("id"),
        )
        if error:
            module.fail_json(msg=f"Error deleting C2C IP Range: {to_native(error)}")
        module.exit_json(changed=True, data=existing_range)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        ip_range_begin=dict(type="str", required=False),
        ip_range_end=dict(type="str", required=False),
        location=dict(type="str", required=False),
        location_hint=dict(type="str", required=False),
        sccm_flag=dict(type="bool", required=False),
        subnet_cidr=dict(type="str", required=False),
        country_code=dict(type="str", required=False),
        latitude_in_db=dict(type="str", required=False),
        longitude_in_db=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
