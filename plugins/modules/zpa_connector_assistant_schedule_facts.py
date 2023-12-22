#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: zpa_connector_assistant_schedule_facts
short_description: Gets the Auto Delete frequency of the App Connector.
version_added: "1.0.0"
description:
    - Gets the Auto Delete frequency configuration of the App Connector.
author:
    - William Guilherme (@willguibr)
requirements:
    - Zscaler SDK Python can be obtained from PyPI (https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
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
"""

EXAMPLES = r"""
- name: Gather Details of All Assistant Schedules
  zscaler.zpacloud.zpa_connector_assistant_schedule_facts:
    provider: "{{ zpa_cloud }}"

- name: Gather Details of Assistant Schedules by ID
  zscaler.zpacloud.zpa_connector_assistant_schedule_facts:
    provider: "{{ zpa_cloud }}"
    id: '1'

- name: Gather Details of Assistant Schedules by Customer ID
  zscaler.zpacloud.zpa_connector_assistant_schedule_facts:
    provider: "{{ zpa_cloud }}"
    customer_id: "216196257331282583"
"""

RETURN = r"""
# Default return values
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
    client = ZPAClientHelper(module)

    # Query by schedule_id if provided, else query by customer_id
    if schedule_id:
        schedule = client.connectors.get_connector_schedule(schedule_id=schedule_id)
        if schedule is None:
            module.fail_json(
                msg=f"Failed to retrieve schedule assistant by ID: '{schedule_id}'"
            )
        module.exit_json(changed=False, schedule=schedule)
    elif customer_id:
        schedule = client.connectors.get_connector_schedule(customer_id=customer_id)
        if schedule is None:
            module.fail_json(
                msg=f"Failed to retrieve schedule assistant by customer ID: '{customer_id}'"
            )
        module.exit_json(changed=False, schedule=schedule)
    else:
        module.fail_json(msg="Either 'id' or 'customer_id' must be provided.")


def main():
    env_customer_id = os.getenv("ZPA_CUSTOMER_ID")

    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        customer_id=dict(type="str", required=False, default=env_customer_id),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
