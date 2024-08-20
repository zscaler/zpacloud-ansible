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
module: zpa_server_group_info
short_description: Retrieves information about an server group
description:
    - This module will allow the retrieval of information about a server group resource.
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
     - Name of the server group.
    required: false
    type: str
  id:
    description:
     - ID of the server group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Details of All Server Groups
  zscaler.zpacloud.zpa_server_group_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific Server Group by Name
  zscaler.zpacloud.zpa_server_group_facts:
    provider: "{{ zpa_cloud }}"
    name: Example

- name: Get Details of a Specific Server Group by ID
  zscaler.zpacloud.zpa_server_group_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331291969"
"""

RETURN = r"""
groups:
  description: >-
    A list of dictionaries containing details about the server groups.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the server group.
      type: str
      sample: "216199618143442001"
    name:
      description: The name of the server group.
      type: str
      sample: "Example200"
    description:
      description: A brief description of the server group.
      type: str
      sample: "Example200"
    enabled:
      description: Indicates whether the server group is enabled.
      type: bool
      sample: true
    config_space:
      description: The configuration space where the server group resides.
      type: str
      sample: "DEFAULT"
    dynamic_discovery:
      description: Indicates if dynamic discovery is enabled for the server group.
      type: bool
      sample: true
    ip_anchored:
      description: Indicates if the server group is IP anchored.
      type: bool
      sample: false
    microtenant_name:
      description: The name of the microtenant associated with the server group.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the server group.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The timestamp when the server group was last modified.
      type: str
      sample: "1724111999"
    creation_time:
      description: The timestamp when the server group was created.
      type: str
      sample: "1724111999"
    app_connector_groups:
      description: A list of dictionaries containing details about the associated app connector groups.
      type: list
      elements: dict
      contains:
        id:
          description: The unique identifier of the app connector group.
          type: str
          sample: "216199618143441990"
        name:
          description: The name of the app connector group.
          type: str
          sample: "test_zpa_app_connector_group_2n8Cq"
        description:
          description: A brief description of the app connector group.
          type: str
          sample: "test_zpa_app_connector_group_2n8Cq"
        enabled:
          description: Indicates whether the app connector group is enabled.
          type: bool
          sample: true
        city_country:
          description: The city and country where the app connector group is located.
          type: str
          sample: "San Jose, US"
        country_code:
          description: The country code of the app connector group location.
          type: str
          sample: "US"
        location:
          description: The specific location details of the app connector group.
          type: str
          sample: "San Jose, CA, USA"
        dns_query_type:
          description: The DNS query type used by the app connector group.
          type: str
          sample: "IPV4_IPV6"
        lss_app_connector_group:
          description: Indicates if the app connector group is used for LSS (Log Streaming Service).
          type: bool
          sample: false
        override_version_profile:
          description: Indicates if the version profile override is enabled.
          type: bool
          sample: true
        pra_enabled:
          description: Indicates if the app connector group has Private Routing Architecture (PRA) enabled.
          type: bool
          sample: false
        tcp_quick_ack_app:
          description: Indicates if TCP Quick ACK is enabled for the application.
          type: bool
          sample: false
        tcp_quick_ack_assistant:
          description: Indicates if TCP Quick ACK is enabled for the assistant.
          type: bool
          sample: false
        tcp_quick_ack_read_assistant:
          description: Indicates if TCP Quick ACK is enabled for reading assistant.
          type: bool
          sample: false
        use_in_dr_mode:
          description: Indicates if the app connector group is used in disaster recovery mode.
          type: bool
          sample: false
        version_profile_id:
          description: The version profile ID associated with the app connector group.
          type: str
          sample: "0"
        waf_disabled:
          description: Indicates if Web Application Firewall (WAF) is disabled.
          type: bool
          sample: false
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    group_id = module.params.get("id", None)
    group_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    groups = []
    if group_id is not None:
        group_box = client.server_groups.get_group(group_id=group_id)
        if group_box is None:
            module.fail_json(
                msg="Failed to retrieve Server Group ID: '%s'" % (group_id)
            )
        groups = [group_box.to_dict()]
    else:
        groups = client.server_groups.list_groups(pagesize=500).to_list()
        if group_name is not None:
            group_found = False
            for group in groups:
                if group.get("name") == group_name:
                    group_found = True
                    groups = [group]
            if not group_found:
                module.fail_json(
                    msg="Failed to retrieve Server Group Name: '%s'" % (group_name)
                )
    module.exit_json(changed=False, groups=groups)


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
