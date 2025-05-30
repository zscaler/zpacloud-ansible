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

DOCUMENTATION = r"""
---
module: zpa_connector_assistant_schedule_info
short_description: Gets the Auto Delete frequency of the App Connector.
version_added: "1.0.0"
description:
    - Gets the Auto Delete frequency configuration of the App Connector.
author:
    - William Guilherme (@willguibr)
requirements:
    - Zscaler SDK Python can be obtained from PyPI (https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  id:
      description:
          - The unique identifier for the App Connector auto deletion configuration for a customer.
          - This field is only required for the PUT request to update the frequency of the App Connector Settings.
      type: str
  customer_id:
      description:
          - The unique identifier of the ZPA tenant
      type: str
      required: false
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Gather Details of All Assistant Schedules
  zscaler.zpacloud.zpa_connector_assistant_schedule_info:
    provider: "{{ zpa_cloud }}"

- name: Gather Details of Assistant Schedules by ID
  zscaler.zpacloud.zpa_connector_assistant_schedule_info:
    provider: "{{ zpa_cloud }}"
    id: '1'

- name: Gather Details of Assistant Schedules by Customer ID
  zscaler.zpacloud.zpa_connector_assistant_schedule_info:
    provider: "{{ zpa_cloud }}"
    customer_id: "216196257331282583"
"""

RETURN = r"""
schedule:
  description: Details of the Auto Delete frequency configuration of the App Connector.
  returned: always
  type: dict
  contains:
    customer_id:
      description: The unique identifier of the ZPA tenant.
      type: str
      sample: "216199618143191040"
    delete_disabled:
      description: Indicates whether the auto deletion feature is disabled.
      type: bool
      sample: true
    enabled:
      description: Indicates whether the auto deletion feature is enabled.
      type: bool
      sample: false
    frequency:
      description: The frequency of the auto deletion (e.g., days, weeks).
      type: str
      sample: "days"
    frequency_interval:
      description: The interval at which the auto deletion occurs.
      type: str
      sample: "7"
    id:
      description: The unique identifier of the auto deletion schedule.
      type: str
      sample: "5"

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
import os
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    schedule_id = module.params.get("id")
    customer_id = module.params.get("customer_id")
    microtenant_id = module.params.get("microtenant_id")
    client = ZPAClientHelper(module)

    query_params = {}
    if microtenant_id:
        query_params["microtenantId"] = microtenant_id

    # Always fetch the schedule (only one is returned by the API)
    result, _unused, error = client.app_connector_schedule.get_connector_schedule(
        customer_id=customer_id
    )
    if error or result is None:
        module.fail_json(
            msg=f"Failed to retrieve App Connector Schedule for customer ID: '{customer_id}'"
        )

    # If ID is provided, manually validate
    if schedule_id:
        schedule_data = result.as_dict() if hasattr(result, "as_dict") else result
        if str(schedule_data.get("id")) != str(schedule_id):
            module.fail_json(
                msg=f"No App Connector Schedule found with ID '{schedule_id}'"
            )
        module.exit_json(changed=False, data=[schedule_data])

    # Otherwise, return the schedule as-is
    module.exit_json(
        changed=False, data=[result.as_dict() if hasattr(result, "as_dict") else result]
    )


def main():
    env_customer_id = os.getenv("ZPA_CUSTOMER_ID")

    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        customer_id=dict(type="str", required=False, default=env_customer_id),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
