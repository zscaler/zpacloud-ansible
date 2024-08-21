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
module: zpa_service_edge_groups
short_description: Create an Service Edge Group in the ZPA Cloud.
description:
  - This module creates/update/delete an Service Edge Group in the ZPA Cloud.
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
    description:
      - The unique identifier of the ZPA Private Service Edge Group.
    required: false
    type: str
  name:
    description:
      - Name of the Service Edge Group.
    required: true
    type: str
  description:
    description: Description of the Service Edge Group.
    required: false
    type: str
  city_country:
    description:
        - City Country of the Service Edge Group.
    type: str
  country_code:
    description:
      - Country code of the Service Edge Group.
    type: str
  enabled:
    description:
      - Whether this Service Edge Group is enabled or not.
    type: bool
  latitude:
    description:
      - Latitude of the Service Edge Group. Integer or decimal. With values in the range of -90 to 90.
    required: false
    type: str
  location:
    description:
      - Location of the Service Edge Group.
    required: false
    type: str
  longitude:
    description:
      - Longitude of the Service Edge Group. Integer or decimal. With values in the range of -180 to 180.
    required: false
    type: str
  upgrade_day:
    description:
      - Service Edge Group in this group will attempt to update to a newer version of the software during this specified day.
      - List of valid days (i.e., Sunday, Monday).
    default: SUNDAY
    type: str
    choices: ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
  upgrade_time_in_secs:
    description:
      - Service Edge Group  in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    default: '66600'
    type: str
  override_version_profile:
    description:
      - Service Edge Group  in this group will attempt to update to a newer version of the software during this specified time.
      - Integer in seconds (i.e., -66600). The integer should be greater than or equal to 0 and less than 86400, in 15 minute intervals.
    required: false
    type: bool
  version_profile_id:
    description:
      - ID of the version profile. To learn more, see Version Profile Use Cases.
      - This value is required, if the value for overrideVersionProfile is set to true.
    required: false
    type: str
    default: '0'
    choices:
      - '0'
      - '1'
      - '2'
  use_in_dr_mode:
    description:
      - Whether or not the Service Edge Group is designated for disaster recovery.
    required: false
    type: bool
  is_public:
    description:
      - Whether or not the ZPA Private Service Edge Group is public.
    required: false
    type: bool
  grace_distance_enabled:
    description:
      - If enabled, allows ZPA Private Service Edge Groups within the specified distance to be prioritized over a closer ZPA Public Service Edge.
    required: false
    type: bool
    default: false
  grace_distance_value:
    description:
      - Indicates the maximum distance in miles or kilometers to ZPA Private Service Edge groups that would override a ZPA Public Service Edge.
    required: false
    type: str
  grace_distance_value_unit:
    description:
      - Indicates the grace distance unit of measure in miles or kilometers.
      - This value is only required if graceDistanceEnabled is set to true.
    required: false
    type: str
    choices:
      - MILES
      - KMS
  trusted_networks_ids:
    description:
      - The list of trusted networks in the ZPA Private Service Edge Group.
    type: list
    elements: str
    required: false
"""

EXAMPLES = """
- name: Create/Update/Delete an Service Edge Group
  zscaler.zpacloud.zpa_service_edge_groups:
    provider: "{{ zpa_cloud }}"
    name: "Example"
    description: "Example2"
    enabled: true
    is_public: true
    city_country: "California, US"
    country_code: "US"
    latitude: "37.3382082"
    longitude: "-121.8863286"
    location: "San Jose, CA, USA"
    upgrade_day: "SUNDAY"
    upgrade_time_in_secs: "66600"
    override_version_profile: true
    version_profile_id: "0"
"""

RETURN = """
# The newly created Service Edge Group resource record.
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    validate_latitude,
    validate_longitude,
    diff_suppress_func_coordinate,
    deleteNone,
    normalize_app,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)

    latitude = module.params.get("latitude")
    longitude = module.params.get("longitude")

    # Convert boolean is_public to string 'TRUE' or 'FALSE' if it is not None
    is_public = module.params.get("is_public")
    is_public_str = "TRUE" if is_public else "FALSE" if is_public is not None else None

    group = dict()
    params = [
        "id",
        "name",
        "description",
        "enabled",
        "city_country",
        "country_code",
        "latitude",
        "longitude",
        "location",
        "upgrade_day",
        "upgrade_time_in_secs",
        "override_version_profile",
        "version_profile_id",
        "use_in_dr_mode",
        "is_public",
        "grace_distance_enabled",
        "grace_distance_value",
        "grace_distance_value_unit",
        "trusted_networks_ids",
    ]
    for param_name in params:
        group[param_name] = module.params.get(param_name, None)

    group["is_public"] = is_public_str

    group_id = group.get("id", None)
    group_name = group.get("name", None)

    existing_group = None
    if group_id is not None:
        group_box = client.service_edges.get_service_edge_group(group_id=group_id)
        if group_box is not None:
            existing_group = group_box.to_dict()
    elif group_name is not None:
        groups = client.service_edges.list_service_edge_groups().to_list()
        for group_ in groups:
            if group_.get("name") == group_name:
                existing_group = group_

    # Normalize and compare existing and desired data
    desired_group = normalize_app(group)
    current_group = normalize_app(existing_group) if existing_group else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_group.items():
        if key not in fields_to_exclude and current_group.get(key) != value:
            differences_detected = True
            # module.warn(
            #     f"Difference detected in {key}. Current: {current_group.get(key)}, Desired: {value}"
            # )

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_group is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_group is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_group is not None:
        id = existing_group.get("id")
        existing_group.update(group)
        existing_group["id"] = id

    if state == "present":
        if latitude is not None and longitude is not None:
            unused_result_lat, lat_errors = validate_latitude(latitude)
            unused_result_lon, lon_errors = validate_longitude(longitude)
            if lat_errors:
                module.fail_json(msg="; ".join(lat_errors))
            if lon_errors:
                module.fail_json(msg="; ".join(lon_errors))

        if existing_group is not None:
            if differences_detected:
                """Update"""
                # Check if latitude and longitude need to be updated
                existing_lat = existing_group.get("latitude")
                new_lat = group.get("latitude")
                if new_lat is not None:  # Check if new_lat is not None before comparing
                    if diff_suppress_func_coordinate(existing_lat, new_lat):
                        existing_group["latitude"] = (
                            existing_lat  # reset to original if they're deemed equal
                        )
                else:
                    existing_group["latitude"] = (
                        existing_lat  # If new_lat is None, keep the existing value
                    )

                existing_long = existing_group.get("longitude")
                new_long = group.get("longitude")
                if (
                    new_long is not None
                ):  # Check if new_long is not None before comparing
                    if diff_suppress_func_coordinate(existing_long, new_long):
                        existing_group["longitude"] = (
                            existing_long  # reset to original if they're deemed equal
                        )
                else:
                    existing_group["longitude"] = (
                        existing_long  # If new_long is None, keep the existing value
                    )

                existing_group = deleteNone(
                    dict(
                        group_id=existing_group.get("id", None),
                        name=existing_group.get("name", None),
                        description=existing_group.get("description", None),
                        enabled=existing_group.get("enabled", None),
                        city_country=existing_group.get("city_country", None),
                        country_code=existing_group.get("country_code", None),
                        latitude=existing_group.get("latitude", None),
                        longitude=existing_group.get("longitude", None),
                        location=existing_group.get("location", None),
                        upgrade_day=existing_group.get("upgrade_day", None),
                        is_public=existing_group.get("is_public", None),
                        upgrade_time_in_secs=existing_group.get(
                            "upgrade_time_in_secs", None
                        ),
                        override_version_profile=existing_group.get(
                            "override_version_profile", None
                        ),
                        version_profile_id=existing_group.get(
                            "version_profile_id", None
                        ),
                        use_in_dr_mode=existing_group.get("use_in_dr_mode", None),
                        grace_distance_enabled=existing_group.get(
                            "grace_distance_enabled", None
                        ),
                        grace_distance_value=existing_group.get(
                            "grace_distance_value", None
                        ),
                        grace_distance_value_unit=existing_group.get(
                            "grace_distance_value_unit", None
                        ),
                    )
                )
                existing_group = client.service_edges.update_service_edge_group(
                    **existing_group
                ).to_dict()
                module.exit_json(changed=True, data=existing_group)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_group)
        else:
            """Create"""
            normalized_group = deleteNone(
                dict(
                    name=group.get("name", None),
                    description=group.get("description", None),
                    enabled=group.get("enabled", None),
                    city_country=group.get("city_country", None),
                    country_code=group.get("country_code", None),
                    latitude=group.get("latitude", None),
                    longitude=group.get("longitude", None),
                    location=group.get("location", None),
                    upgrade_day=group.get("upgrade_day", None),
                    is_public=group.get("is_public", None),
                    upgrade_time_in_secs=group.get("upgrade_time_in_secs", None),
                    override_version_profile=group.get(
                        "override_version_profile", None
                    ),
                    version_profile_id=group.get("version_profile_id", None),
                    use_in_dr_mode=group.get("use_in_dr_mode", None),
                    grace_distance_enabled=group.get("grace_distance_enabled", None),
                    grace_distance_value=group.get("grace_distance_value", None),
                    grace_distance_value_unit=group.get(
                        "grace_distance_value_unit", None
                    ),
                )
            )
            group = client.service_edges.add_service_edge_group(
                **normalized_group
            ).to_dict()
            module.exit_json(changed=True, data=group)
    elif (
        state == "absent"
        and existing_group is not None
        and existing_group.get("id") is not None
    ):
        code = client.service_edges.delete_service_edge_group(
            group_id=existing_group.get("id")
        )
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_group)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        city_country=dict(type="str", required=False),
        country_code=dict(type="str", required=False),
        is_public=dict(type="bool", required=False),
        latitude=dict(type="str", required=False),
        location=dict(type="str", required=False),
        longitude=dict(type="str", required=False),
        upgrade_day=dict(
            type="str",
            choices=[
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            ],
            default="SUNDAY",
            required=False,
        ),
        upgrade_time_in_secs=dict(type="str", default="66600"),
        override_version_profile=dict(type="bool", required=False),
        version_profile_id=dict(type="str", choices=["0", "1", "2"], default="0"),
        use_in_dr_mode=dict(type="bool", required=False),
        grace_distance_enabled=dict(type="bool", required=False, default=False),
        grace_distance_value=dict(type="str", required=False),
        grace_distance_value_unit=dict(
            type="str", required=False, choices=["MILES", "KMS"]
        ),
        trusted_networks_ids=dict(type="list", elements="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
