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
module: zpa_application_segment_weightedlb_config
short_description: Manage Weighted Load Balancing Config for an Application Segment.
description:
    - This module will update the Weighted Load Balancing configuration for an Application Segment.
    - Weighted Load Balancing allows you to distribute traffic across server groups based on assigned weights.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is supported.
    - This module only supports update operations. Use the info module to retrieve current configuration.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  application_id:
    description:
     - Application segment identifier to configure. One of application_id or application_name must be provided.
    required: false
    type: str
  application_name:
    description:
     - Application segment name to configure. One of application_id or application_name must be provided.
    required: false
    type: str
  weighted_load_balancing:
    description:
     - Flag to enable or disable weighted load balancing on the segment.
    required: false
    type: bool
  application_to_server_group_mappings:
    description:
     - A list of mappings that define server groups and their associated weights and passive flags.
    required: false
    type: list
    elements: dict
    suboptions:
      id:
        description: The ID of the server group.
        type: str
        required: true
      weight:
        description: The weight assigned to this server group.
        type: str
        required: false
      passive:
        description: Indicates whether the server group operates in passive mode.
        type: bool
        required: false
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      required: false
      type: str
"""

EXAMPLES = """
- name: Update Weighted LB Config for Application Segment
  zscaler.zpacloud.zpa_application_segment_weightedlb_config:
    provider: "{{ zpa_cloud }}"
    application_id: "72058304855090129"
    weighted_load_balancing: true
    application_to_server_group_mappings:
      - id: "72058304855090128"
        weight: "10"
        passive: true
      - id: "72058304855047747"
        weight: "20"
        passive: false

- name: Update Weighted LB Config by Application Name
  zscaler.zpacloud.zpa_application_segment_weightedlb_config:
    provider: "{{ zpa_cloud }}"
    application_name: "MyAppSegment"
    weighted_load_balancing: true
    application_to_server_group_mappings:
      - id: "72058304855090128"
        weight: "10"
        passive: false
"""

RETURN = """
# The updated Weighted Load Balancing configuration for the Application Segment.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
)
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
    weighted_load_balancing = module.params.get("weighted_load_balancing")
    application_to_server_group_mappings = module.params.get("application_to_server_group_mappings")
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

    # Get current config for drift detection
    current_config, _unused, error = client.application_segment.get_weighted_lb_config(
        application_id, query_params
    )
    if error:
        module.fail_json(
            msg=f"Failed to retrieve current Weighted LB Config for application '{application_id}': {to_native(error)}"
        )

    current_dict = current_config.as_dict() if current_config else {}

    # Determine drift
    drift = False
    if weighted_load_balancing is not None:
        if current_dict.get("weighted_load_balancing") != weighted_load_balancing:
            drift = True

    if application_to_server_group_mappings is not None:
        current_mappings = current_dict.get("application_to_server_group_mappings", [])
        # Simple comparison - check if mappings are different
        if len(current_mappings) != len(application_to_server_group_mappings):
            drift = True
        else:
            # Compare each mapping
            current_map_dict = {m.get("id"): m for m in current_mappings}
            for new_mapping in application_to_server_group_mappings:
                current_m = current_map_dict.get(new_mapping.get("id"))
                if not current_m:
                    drift = True
                    break
                if new_mapping.get("weight") and str(current_m.get("weight")) != str(new_mapping.get("weight")):
                    drift = True
                    break
                if new_mapping.get("passive") is not None and current_m.get("passive") != new_mapping.get("passive"):
                    drift = True
                    break

    if module.check_mode:
        module.exit_json(changed=drift)

    if drift:
        # Build payload
        payload = deleteNone({
            "weighted_load_balancing": weighted_load_balancing,
            "application_to_server_group_mappings": application_to_server_group_mappings,
        })

        updated, _unused, error = client.application_segment.update_weighted_lb_config(
            segment_id=application_id,
            query_params=query_params,
            **payload
        )
        if error:
            module.fail_json(
                msg=f"Error updating Weighted LB Config: {to_native(error)}"
            )

        result = updated.as_dict() if updated else {}
        result["application_id"] = application_id
        if application_name:
            result["application_name"] = application_name
        module.exit_json(changed=True, data=result)
    else:
        result = current_dict
        result["application_id"] = application_id
        if application_name:
            result["application_name"] = application_name
        module.exit_json(changed=False, data=result)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        application_id=dict(type="str", required=False),
        application_name=dict(type="str", required=False),
        weighted_load_balancing=dict(type="bool", required=False),
        application_to_server_group_mappings=dict(
            type="list",
            elements="dict",
            required=False,
            options=dict(
                id=dict(type="str", required=True),
                weight=dict(type="str", required=False),
                passive=dict(type="bool", required=False),
            ),
        ),
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
