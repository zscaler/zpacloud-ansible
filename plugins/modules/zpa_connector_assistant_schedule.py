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
module: zpa_connector_assistant_schedule
short_description: Configures Auto Delete for the specified disconnected App Connector
description:
    - This module will configure Auto Delete for the specified disconnected App Connector
author:
    - William Guilherme (@willguibr)
version_added: '1.0.0'
requirements:
    - Zscaler SDK Python can be obtained from PyPI (https://pypi.org/project/zscaler-sdk-python/)

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
    delete_disabled:
        description:
            - Indicates if the App Connectors are included for deletion if they are in a disconnected state based on frequencyInterval and frequency values
        type: bool
    enabled:
        description:
            - Indicates if the setting for deleting App Connectors is enabled or disabled.
        type: bool
    frequency:
        description:
            - The scheduled frequency at which the disconnected App Connectors are deleted
        type: str
        default: days
    frequency_interval:
        description:
            - The interval for the configured frequency value. The minimum supported value is 5.
        type: str
        default: '5'
        choices: ['5', '7', '14', '30', '60', '90']
    state:
        description:
            - The state of the module, which determines if the settings are to be applied.
        type: str
        choices: ['present']
        default: 'present'
"""

EXAMPLES = r"""
- name: Enable or Update Auto Delete for disconnected App Connector
  zscaler.zpacloud.zpa_connector_assistant_schedule:
    provider: '{{ zpa_cloud }}'
    customer_id: "1234567895452"
    enabled: true
    delete_disabled: true
    frequency: "days"
    frequency_interval: "5"
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
    state = module.params.get("state")
    customer_id = module.params.get("customer_id")
    enabled = module.params.get("enabled")
    delete_disabled = module.params.get("delete_disabled")
    frequency = module.params.get("frequency")
    frequency_interval = module.params.get("frequency_interval")

    client = ZPAClientHelper(module)

    # Ensure we only handle the 'present' state
    if state != "present":
        module.fail_json(msg="This module only supports the state 'present'.")

    # Attempt to get the current schedule
    try:
        schedule = client.connectors.get_connector_schedule(customer_id=customer_id)
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve schedule: {to_native(e)}")

    if not schedule:
        # Create a new schedule if none exists and 'enabled' is True
        if enabled:
            try:
                response = client.connectors.add_connector_schedule(
                    frequency=frequency,
                    interval=frequency_interval,
                    disabled=delete_disabled,
                    customer_id=customer_id,
                    enabled=enabled,
                )
                module.exit_json(
                    changed=True,
                    message="Schedule created successfully.",
                    data=response.to_dict(),
                )
            except Exception as e:
                module.fail_json(msg=f"Failed to create schedule: {to_native(e)}")
        else:
            module.exit_json(
                changed=False, message="No schedule exists and creation is not enabled."
            )
    else:
        # If schedule exists, check if updates are necessary
        scheduler_id = schedule.get("id")
        updates_needed = {}
        for key, desired_value in [
            ("enabled", enabled),
            ("delete_disabled", delete_disabled),
            ("frequency", frequency),
            ("frequency_interval", frequency_interval),
        ]:
            if schedule.get(key) != desired_value:
                updates_needed[key] = desired_value

        if updates_needed:
            # Update the schedule if there are changes
            try:
                result = client.connectors.update_connector_schedule(
                    scheduler_id=scheduler_id, customer_id=customer_id, **updates_needed
                )
                if result:
                    module.exit_json(
                        changed=True, message="Schedule updated successfully."
                    )
                else:
                    module.fail_json(
                        msg="Failed to update schedule: Update not successful."
                    )
            except Exception as e:
                module.fail_json(msg=f"Failed to update schedule: {to_native(e)}")
        else:
            module.exit_json(
                changed=False,
                message="No updates required; schedule remains unchanged.",
            )


def main():
    # Retrieve customer_id from the environment variable if available
    env_customer_id = os.getenv("ZPA_CUSTOMER_ID")

    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        customer_id=dict(type="str", required=False, default=env_customer_id),
        enabled=dict(type="bool", required=False),
        delete_disabled=dict(type="bool", required=False),
        frequency=dict(type="str", required=False, default="days"),
        frequency_interval=dict(
            type="str",
            required=False,
            default="5",
            choices=["5", "7", "14", "30", "60", "90"],
        ),
        state=dict(type="str", choices=["present"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
