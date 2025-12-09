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
module: zpa_private_cloud_group
short_description: Create a Private Cloud Group
description:
    - This module will create/update/delete a Private Cloud Group resource.
    - Private Cloud Groups represent geographic locations where Private Cloud Controllers are deployed.
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
    description: "The unique identifier of the Private Cloud Group"
    type: str
    required: false
  name:
    description: "Name of the Private Cloud Group"
    type: str
    required: true
  description:
    description: "Description of the Private Cloud Group"
    type: str
    required: false
  enabled:
    description: "Whether this Private Cloud Group is enabled or not"
    type: bool
    required: false
  city_country:
    description: "City and country of the Private Cloud Group. Format: <City>, <Country Code> (e.g., Sydney, AU)"
    type: str
    required: false
  country_code:
    description: "Country code of the Private Cloud Group (ISO standard)"
    type: str
    required: false
  is_public:
    description: "Whether the Private Cloud Group is public"
    type: str
    required: false
  latitude:
    description: "Latitude of the Private Cloud Group location. Integer or decimal with values in the range of -90 to 90"
    type: str
    required: false
  location:
    description: "Location name of the Private Cloud Group"
    type: str
    required: false
  longitude:
    description: "Longitude of the Private Cloud Group location. Integer or decimal with values in the range of -180 to 180"
    type: str
    required: false
  override_version_profile:
    description: "Whether the default version profile of the Private Cloud Group is applied or overridden"
    type: bool
    required: false
  site_id:
    description: "Site ID for the Private Cloud Group"
    type: str
    required: false
  upgrade_day:
    description: "Private Cloud Controllers in this group will attempt to update during this specified day"
    type: str
    required: false
    choices: ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
  upgrade_time_in_secs:
    description: "Private Cloud Controllers will attempt to update during this specified time. Integer in seconds (i.e., -66600). Must be >= 0 and < 86400, in 15 minute intervals"
    type: str
    required: false
  version_profile_id:
    description: "ID of the version profile for the Private Cloud Group"
    type: str
    required: false
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
      required: false
      type: str
"""

EXAMPLES = """
- name: Create/Update/Delete a Private Cloud Group
  zscaler.zpacloud.zpa_private_cloud_group:
    provider: "{{ zpa_cloud }}"
    name: US East Private Cloud
    description: Private Cloud Group for US East region
    enabled: true
    city_country: "San Jose, US"
    country_code: "US"
    latitude: "37.3382082"
    longitude: "-121.8863286"
    location: "San Jose, CA, USA"
    upgrade_day: "SUNDAY"
"""

RETURN = """
# The newly created Private Cloud Group resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    normalize_app,
    collect_all_items,
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
        "city_country",
        "country_code",
        "is_public",
        "latitude",
        "location",
        "longitude",
        "override_version_profile",
        "site_id",
        "upgrade_day",
        "upgrade_time_in_secs",
        "version_profile_id",
        "microtenant_id",
    ]
    group_data = {param: module.params.get(param) for param in params}
    group_id = group_data.get("id")
    group_name = group_data.get("name")
    microtenant_id = group_data.get("microtenant_id")

    # Step 1: Fetch existing group if possible
    existing_group = None
    if group_id:
        result, _unused, error = client.private_cloud_group.get_cloud_group(
            group_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving Private Cloud Group by ID {group_id}: {to_native(error)}"
            )
        if result:
            existing_group = result.as_dict()

    elif group_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        group_list, error = collect_all_items(
            client.private_cloud_group.list_cloud_groups, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing Private Cloud Groups: {to_native(error)}")
        for item in group_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == group_name:
                existing_group = item_dict
                break

    # Step 2: Normalize and compare
    desired_group = normalize_app(group_data)
    current_group = normalize_app(existing_group) if existing_group else {}

    # Fields to ignore in drift detection
    fields_to_ignore = ["id", "microtenant_id"]

    # Helper function to normalize empty values for comparison
    def normalize_value(val):
        if val is None or val == "" or val == []:
            return None
        return val

    # Check drift only for fields that have actual (non-None) values in desired state
    drift = False
    for k in desired_group:
        if k in fields_to_ignore:
            continue
        desired_val = normalize_value(desired_group.get(k))
        current_val = normalize_value(current_group.get(k))
        # Only check drift if desired value is explicitly set (not None)
        if desired_val is not None and desired_val != current_val:
            drift = True
            break

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_group))
            or (state == "absent" and existing_group)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_group:
            if drift:
                update_group = deleteNone(
                    {
                        "microtenant_id": desired_group.get("microtenant_id"),
                        "name": desired_group.get("name"),
                        "description": desired_group.get("description"),
                        "enabled": desired_group.get("enabled"),
                        "city_country": desired_group.get("city_country"),
                        "country_code": desired_group.get("country_code"),
                        "is_public": desired_group.get("is_public"),
                        "latitude": desired_group.get("latitude"),
                        "location": desired_group.get("location"),
                        "longitude": desired_group.get("longitude"),
                        "override_version_profile": desired_group.get("override_version_profile"),
                        "site_id": desired_group.get("site_id"),
                        "upgrade_day": desired_group.get("upgrade_day"),
                        "upgrade_time_in_secs": desired_group.get("upgrade_time_in_secs"),
                        "version_profile_id": desired_group.get("version_profile_id"),
                    }
                )
                updated, _unused, error = client.private_cloud_group.update_cloud_group(
                    group_id=existing_group.get("id"), **update_group
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating Private Cloud Group: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_group)
        else:
            payload = deleteNone(
                {
                    "microtenant_id": desired_group.get("microtenant_id"),
                    "name": desired_group.get("name"),
                    "description": desired_group.get("description"),
                    "enabled": desired_group.get("enabled"),
                    "city_country": desired_group.get("city_country"),
                    "country_code": desired_group.get("country_code"),
                    "is_public": desired_group.get("is_public"),
                    "latitude": desired_group.get("latitude"),
                    "location": desired_group.get("location"),
                    "longitude": desired_group.get("longitude"),
                    "override_version_profile": desired_group.get("override_version_profile"),
                    "site_id": desired_group.get("site_id"),
                    "upgrade_day": desired_group.get("upgrade_day"),
                    "upgrade_time_in_secs": desired_group.get("upgrade_time_in_secs"),
                    "version_profile_id": desired_group.get("version_profile_id"),
                }
            )
            created, _unused, error = client.private_cloud_group.add_cloud_group(**payload)
            if error:
                module.fail_json(
                    msg=f"Error creating Private Cloud Group: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_group and existing_group.get("id"):
        _unused, _unused, error = client.private_cloud_group.delete_cloud_group(
            group_id=existing_group.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting Private Cloud Group: {to_native(error)}")
        module.exit_json(changed=True, data=existing_group)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        city_country=dict(type="str", required=False),
        country_code=dict(type="str", required=False),
        is_public=dict(type="str", required=False),
        latitude=dict(type="str", required=False),
        location=dict(type="str", required=False),
        longitude=dict(type="str", required=False),
        override_version_profile=dict(type="bool", required=False),
        site_id=dict(type="str", required=False),
        upgrade_day=dict(
            type="str",
            required=False,
            choices=["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"],
        ),
        upgrade_time_in_secs=dict(type="str", required=False),
        version_profile_id=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()

