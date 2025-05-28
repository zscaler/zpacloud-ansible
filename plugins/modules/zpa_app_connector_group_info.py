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
module: zpa_app_connector_group_info
short_description: Retrieves an app connector group information
description:
  - This module will allow the retrieval of information about an app connector group.
author: William Guilherme (@willguibr)
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
      - ID of the App Connector Group.
    required: false
    type: str
  name:
    description:
      - Name of the App Connector Group.
    required: false
    type: str
"""


EXAMPLES = """
- name: Retrieve All App Connector Groups
  zscaler.zpacloud.zpa_app_connector_group_info:
    provider: "{{ zpa_cloud }}"

- name: Retrieve App Connector Group By Name
  zscaler.zpacloud.zpa_app_connector_group_info:
    provider: "{{ zpa_cloud }}"
    name: 'SJC037_App_Connector_Group'

- name: Retrieve App Connector Group By ID
  zscaler.zpacloud.zpa_app_connector_group_info:
    provider: "{{ zpa_cloud }}"
    name: '123456789'
"""

RETURN = r"""
groups:
  description: >-
    Details of the ZPA App Connector Groups.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the App Connector Group.
      type: str
      returned: always
      sample: "216199618143441990"
    name:
      description: The name of the App Connector Group.
      type: str
      returned: always
      sample: "test_zpa_app_connector_group_2n8Cq"
    description:
      description: The description of the App Connector Group.
      type: str
      returned: always
      sample: "test_zpa_app_connector_group_2n8Cq"
    city_country:
      description: The city and country where the App Connector Group is located.
      type: str
      returned: always
      sample: "San Jose, US"
    country_code:
      description: The country code associated with the App Connector Group's location.
      type: str
      returned: always
      sample: "US"
    creation_time:
      description: The creation time of the App Connector Group in epoch format.
      type: str
      returned: always
      sample: "1724099105"
    modified_time:
      description: The last modified time of the App Connector Group in epoch format.
      type: str
      returned: always
      sample: "1724099105"
    modified_by:
      description: The ID of the user who last modified the App Connector Group.
      type: str
      returned: always
      sample: "216199618143191053"
    location:
      description: The detailed location of the App Connector Group.
      type: str
      returned: always
      sample: "San Jose, CA, USA"
    latitude:
      description: The latitude coordinate of the App Connector Group's location.
      type: str
      returned: always
      sample: "37.33874"
    longitude:
      description: The longitude coordinate of the App Connector Group's location.
      type: str
      returned: always
      sample: "-121.8852525"
    enabled:
      description: Indicates whether the App Connector Group is enabled.
      type: bool
      returned: always
      sample: true
    dns_query_type:
      description: The type of DNS query the App Connector Group supports.
      type: str
      returned: always
      sample: "IPV4_IPV6"
    lss_app_connector_group:
      description: Indicates if the group is an LSS App Connector Group.
      type: bool
      returned: always
      sample: false
    microtenant_name:
      description: The name of the microtenant associated with the App Connector Group.
      type: str
      returned: always
      sample: "Default"
    override_version_profile:
      description: Indicates if the version profile is overridden.
      type: bool
      returned: always
      sample: true
    pra_enabled:
      description: Indicates if Proxy Rule Action (PRA) is enabled for the group.
      type: bool
      returned: always
      sample: false
    tcp_quick_ack_app:
      description: Indicates if TCP Quick ACK is enabled for applications.
      type: bool
      returned: always
      sample: false
    tcp_quick_ack_assistant:
      description: Indicates if TCP Quick ACK is enabled for the assistant.
      type: bool
      returned: always
      sample: false
    tcp_quick_ack_read_assistant:
      description: Indicates if TCP Quick ACK is enabled for reading from the assistant.
      type: bool
      returned: always
      sample: false
    upgrade_day:
      description: The scheduled day for upgrades of the App Connector Group.
      type: str
      returned: always
      sample: "SUNDAY"
    upgrade_priority:
      description: The upgrade priority for the App Connector Group.
      type: str
      returned: always
      sample: "WEEK"
    upgrade_time_in_secs:
      description: The upgrade time in seconds for the App Connector Group.
      type: str
      returned: always
      sample: "66600"
    use_in_dr_mode:
      description: Indicates if the group is used in Disaster Recovery mode.
      type: bool
      returned: always
      sample: false
    version_profile_id:
      description: The version profile ID associated with the App Connector Group.
      type: str
      returned: always
      sample: "0"
    version_profile_name:
      description: The name of the version profile associated with the App Connector Group.
      type: str
      returned: always
      sample: "Default"
    version_profile_visibility_scope:
      description: The visibility scope of the version profile.
      type: str
      returned: always
      sample: "ALL"
    waf_disabled:
      description: Indicates if Web Application Firewall (WAF) is disabled for the group.
      type: bool
      returned: always
      sample: false
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
        result, _unused, error = client.app_connector_groups.get_connector_group(
            group_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve App Connector Group ID '{group_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, groups=[result.as_dict()])

    # If no ID, we fetch all
    group_list, err = collect_all_items(
        client.app_connector_groups.list_connector_groups, query_params
    )
    if err:
        module.fail_json(msg=f"Error retrieving App Connector Groups: {to_native(err)}")

    result_list = [g.as_dict() for g in group_list]

    if group_name:
        matched = next((g for g in result_list if g.get("name") == group_name), None)
        if not matched:
            available = [g.get("name") for g in result_list]
            module.fail_json(
                msg=f"App Connector Group '{group_name}' not found. Available: {available}"
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
