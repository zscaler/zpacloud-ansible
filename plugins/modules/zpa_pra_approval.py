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
module: zpa_pra_approval
short_description: Create a PRA Approval Controller.
description:
  - This module will create/update/delete Privileged Remote Access Approval.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
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
    type: str
    description: "The unique identifier of the privileged approval"
    required: false
  email_ids:
    description: The email address of the user that you are assigning the privileged approval to
    required: false
    type: list
    elements: str
  start_time:
    type: str
    description: "The start date that the user has access to the privileged approval i.e Tue, 07 May 2024 11:05:30 PST"
    required: false
  end_time:
    type: str
    description: The end date that the user no longer has access to the privileged approval i.e Tue, 07 Jun 2024 11:05:30 PST
    required: false
  application_ids:
    description:
      - The unique identifier of the pra application segment.
    type: list
    elements: str
    required: false
  working_hours:
    description: "Privileged Approval WorkHours configuration."
    type: dict
    required: false
    suboptions:
      days:
        description: "The days of the week when the privileged approval is active."
        type: list
        elements: str
        choices:
          - MON
          - TUE
          - WED
          - THU
          - FRI
          - SAT
          - SUN
      start_time:
        description: "The local start time for the privileged approval."
        type: str
        required: false
      start_time_cron:
        description:
            - "The cron expression for the start time of the privileged approval, specifying the exact time of day the approval begins."
            - "Example: '0 15 10 ? * MON-FRI' starts the approval at 10:15 AM on weekdays."
        type: str
        required: false
      end_time:
        description: "The local end time for the privileged approval."
        type: str
        required: false
      end_time_cron:
        description:
            - "The cron expression for the end time of the privileged approval, specifying the exact time of day the approval ends."
            - "Example: '0 0 18 ? * MON-FRI' ends the approval at 6:00 PM on weekdays."
        type: str
        required: false
      time_zone:
        description: "The IANA time zone identifier for the privileged approval's timing."
        type: str
        required: false
"""

EXAMPLES = """
- name: Create PRA Approval
  zscaler.zpacloud.zpa_pra_approval:
    provider: '{{ zpa_cloud }}'
    state: present
    email_ids:
      - 'jdoe@example.com'
    start_time: 'Thu, 09 May 2024 8:00:00 PST'
    end_time: 'Mon, 10 Jun 2024 5:00:00 PST'
    application_ids:
      - '216199618143356658'
      - '216199618143356661'
    working_hours:
      days:
        - 'FRI'
        - 'MON'
        - 'SAT'
        - 'SUN'
        - 'THU'
        - 'TUE'
        - 'WED'
      start_time: '09:00'
      end_time: '17:00'
      start_time_cron: '0 0 16 ? * MON,TUE,WED,THU,FRI,SAT,SUN'
      end_time_cron: '0 0 0 ? * MON,TUE,WED,THU,FRI,SAT,SUN'
      time_zone: 'America/Vancouver'
  register: result
"""

RETURN = """
# The newly created privileged approval resource record.
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_approval(approval):
    """
    Normalize rule data by setting computed values.
    """
    normalized = approval.copy()

    computed_values = [
        # "id",
        # "start_time",
        # "end_time",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    approval = dict()
    params = [
        "id",
        "microtenant_id",
        "email_ids",
        "start_time",
        "end_time",
        "application_ids",
        "working_hours",
        "status",
    ]
    for param_name in params:
        approval[param_name] = module.params.get(param_name, None)

    approval_id = approval.get("id", None)
    email_ids = approval.get(
        "email_ids", None
    )  # We'll search by these if no id is given
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_approval = None

    if approval_id:
        # If user provided an ID, fetch directly by ID
        result, _, error = client.pra_approval.get_approval(
            approval_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching pra approval with id {approval_id}: {to_native(error)}"
            )
        existing_approval = result.as_dict()
    else:
        # Otherwise, retrieve entire list and match on email_ids
        result, error = collect_all_items(
            client.pra_approval.list_approval, query_params
        )
        if error:
            module.fail_json(msg=f"Error pra approvals: {to_native(error)}")

        if result and email_ids:
            for approval_ in result:
                # Compare the sorted lists to see if they match
                # (assuming order doesn't matter, or all must match)
                if sorted(approval_.email_ids or []) == sorted(email_ids or []):
                    existing_approval = approval_.as_dict()
                    break

    desired_approval = normalize_approval(approval)
    current_approval = (
        normalize_approval(existing_approval) if existing_approval else {}
    )

    # 🔧 Normalize current_group: convert app_connector_groups to app_connector_group_ids
    if "applications" in current_approval:
        current_approval["application_ids"] = sorted(
            [
                g.get("id")
                for g in current_approval.get("applications", [])
                if g.get("id")
            ]
        )
        del current_approval["applications"]

    # 🔧 Normalize desired_group: ensure app_connector_group_ids is sorted for accurate comparison
    if "application_ids" in desired_approval and desired_approval["application_ids"]:
        desired_approval["application_ids"] = sorted(
            desired_approval["application_ids"]
        )

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_approval.items():
        if key not in fields_to_exclude and current_approval.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_approval.get(key)}, Desired: {value}"
            )

    if module.check_mode:
        if state == "present" and (existing_approval is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_approval is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_approval is not None:
        # Keep the same structure
        id_ = existing_approval.get("id")
        existing_approval.update(approval)
        existing_approval["id"] = id_

    module.warn(f"Final payload being sent to SDK: {approval}")

    if state == "present":
        if existing_approval is not None:
            if differences_detected:
                # Update
                update_approval = deleteNone(
                    {
                        "approval_id": existing_approval.get("id"),
                        "microtenant_id": desired_approval.get("microtenant_id"),
                        "email_ids": desired_approval.get("email_ids"),
                        "start_time": desired_approval.get("start_time"),
                        "end_time": desired_approval.get("end_time"),
                        "status": desired_approval.get("status"),
                        "application_ids": desired_approval.get("application_ids"),
                        "working_hours": desired_approval.get("working_hours"),
                    }
                )
                module.warn("Payload Update for SDK: {}".format(update_approval))
                updated_approval, _, error = client.pra_approval.update_approval(
                    approval_id=update_approval.get("approval_id"), **existing_approval
                )
                if error:
                    module.fail_json(msg=f"Error updating approval: {to_native(error)}")
                module.exit_json(changed=True, data=updated_approval.as_dict())
            else:
                module.exit_json(changed=False, data=existing_approval)
        else:
            module.warn("Creating pra approval as no existing approval was found")
            # Create
            create_approval = deleteNone(
                {
                    "microtenant_id": desired_approval.get("microtenant_id"),
                    "email_ids": desired_approval.get("email_ids"),
                    "start_time": desired_approval.get("start_time"),
                    "end_time": desired_approval.get("end_time"),
                    "status": desired_approval.get("status"),
                    "application_ids": desired_approval.get("application_ids"),
                    "working_hours": desired_approval.get("working_hours"),
                }
            )
            module.warn(f"Payload for SDK: {create_approval}")
            new_approval, _, error = client.pra_approval.add_approval(**create_approval)
            if error:
                module.fail_json(msg=f"Error creating approval: {to_native(error)}")
            module.exit_json(changed=True, data=new_approval.as_dict())

    elif state == "absent":
        if existing_approval:
            _, _, error = client.pra_approval.delete_approval(
                approval_id=existing_approval.get("id"),
                microtenant_id=microtenant_id,
            )
            if error:
                module.fail_json(msg=f"Error deleting pra approval: {to_native(error)}")
            module.exit_json(changed=True, data=existing_approval)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        email_ids=dict(type="list", elements="str", required=False),
        start_time=dict(type="str", required=False),
        end_time=dict(type="str", required=False),
        status=dict(type="str", required=False),
        application_ids=dict(type="list", elements="str", required=False),
        working_hours=dict(
            type="dict",
            options=dict(
                days=dict(
                    type="list",
                    elements="str",
                    required=False,
                    choices=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
                ),
                start_time=dict(type="str", required=False),
                start_time_cron=dict(type="str", required=False),
                end_time=dict(type="str", required=False),
                end_time_cron=dict(type="str", required=False),
                time_zone=dict(type="str", required=False),
            ),
            required=False,
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
