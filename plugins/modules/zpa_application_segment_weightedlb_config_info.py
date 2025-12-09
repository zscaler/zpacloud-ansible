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
module: zpa_application_segment_weightedlb_config_info
short_description: Retrieves Weighted Load Balancing Config for an Application Segment.
description:
    - This module will allow the retrieval of Weighted Load Balancing configuration for an Application Segment.
    - Weighted Load Balancing allows you to distribute traffic across server groups based on assigned weights.
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
  application_id:
    description:
     - Application segment identifier to query. One of application_id or application_name must be provided.
    required: false
    type: str
  application_name:
    description:
     - Application segment name to query. One of application_id or application_name must be provided.
    required: false
    type: str
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Get Weighted LB Config by Application ID
  zscaler.zpacloud.zpa_application_segment_weightedlb_config_info:
    provider: "{{ zpa_cloud }}"
    application_id: "216196257331291969"

- name: Get Weighted LB Config by Application Name
  zscaler.zpacloud.zpa_application_segment_weightedlb_config_info:
    provider: "{{ zpa_cloud }}"
    application_name: "MyAppSegment"
"""

RETURN = r"""
config:
  description: >-
    A dictionary containing details about the Weighted Load Balancing configuration.
  returned: always
  type: dict
  contains:
    application_id:
      description: The unique identifier of the Application Segment.
      type: str
      sample: "216199618143442000"
    application_name:
      description: The name of the Application Segment.
      type: str
      sample: "MyAppSegment"
    weighted_load_balancing:
      description: Indicates if weighted load balancing is enabled for the application segment.
      type: bool
      sample: true
    application_to_server_group_mappings:
      description: Application to server group mapping details and weights.
      type: list
      elements: dict
      contains:
        id:
          description: Server group mapping identifier.
          type: str
          sample: "216199618143442001"
        name:
          description: Server group name.
          type: str
          sample: "ServerGroup01"
        passive:
          description: Whether the server group is passive.
          type: bool
          sample: false
        weight:
          description: Assigned weight for the server group.
          type: str
          sample: "10"
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

    application_id = module.params.get("application_id")
    application_name = module.params.get("application_name")
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Validate that at least one of application_id or application_name is provided
    if not application_id and not application_name:
        module.fail_json(msg="Either 'application_id' or 'application_name' must be provided")

    # If application_name is provided, resolve it to application_id
    if application_name and not application_id:
        segment_list, err = collect_all_items(
            client.application_segment.list_segments, query_params
        )
        if err:
            module.fail_json(msg=f"Error listing application segments: {to_native(err)}")

        matched_segment = None
        for segment in segment_list:
            segment_dict = segment.as_dict()
            if segment_dict.get("name") == application_name:
                matched_segment = segment_dict
                break

        if not matched_segment:
            available = [s.as_dict().get("name") for s in segment_list]
            module.fail_json(
                msg=f"Application segment '{application_name}' not found. Available: {available}"
            )

        application_id = matched_segment.get("id")

    # Get the weighted load balancer config
    config, _unused, error = client.application_segment.get_weighted_lb_config(
        application_id, query_params
    )
    if error or config is None:
        module.fail_json(
            msg=f"Failed to retrieve Weighted LB Config for application '{application_id}': {to_native(error)}"
        )

    result = config.as_dict()
    result["application_id"] = application_id
    if application_name:
        result["application_name"] = application_name

    module.exit_json(changed=False, config=result)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        application_id=dict(type="str", required=False),
        application_name=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["application_id", "application_name"]],
        required_one_of=[["application_id", "application_name"]],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()

