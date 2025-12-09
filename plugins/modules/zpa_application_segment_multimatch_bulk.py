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
module: zpa_application_segment_multimatch_bulk
short_description: Bulk update multimatch settings for Application Segments.
description:
    - This module allows bulk updating of multimatch (match_style) settings for multiple application segments.
    - The match_style can be set to either EXCLUSIVE or INCLUSIVE for all specified application segments.
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

options:
  application_ids:
    description:
      - List of application segment IDs to update match_style for.
      - At least one application ID must be provided.
    required: true
    type: list
    elements: str
  match_style:
    description:
      - Match style to apply to all specified application segments.
      - EXCLUSIVE means domains are matched exclusively to this segment.
      - INCLUSIVE means domains can be shared with other segments.
    required: true
    type: str
    choices:
      - EXCLUSIVE
      - INCLUSIVE
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant.
    required: false
    type: str
"""

EXAMPLES = """
- name: Update Multiple Application Segments to INCLUSIVE Match Style
  zscaler.zpacloud.zpa_application_segment_multimatch_bulk:
    provider: "{{ zpa_cloud }}"
    application_ids:
      - "216196257331372697"
      - "216196257331372698"
    match_style: "INCLUSIVE"

- name: Update Multiple Application Segments to EXCLUSIVE Match Style
  zscaler.zpacloud.zpa_application_segment_multimatch_bulk:
    provider: "{{ zpa_cloud }}"
    application_ids:
      - "216196257331372697"
    match_style: "EXCLUSIVE"

- name: Update Application Segments with Microtenant
  zscaler.zpacloud.zpa_application_segment_multimatch_bulk:
    provider: "{{ zpa_cloud }}"
    application_ids:
      - "216196257331372697"
      - "216196257331372698"
    match_style: "INCLUSIVE"
    microtenant_id: "216199618143373000"
"""

RETURN = """
# The result of the bulk update operation.
data:
  description: Result message from the bulk update operation.
  returned: always
  type: dict
  contains:
    message:
      description: Status message indicating the result of the operation.
      type: str
      sample: "Bulk update multimatch operation completed successfully."
    application_ids:
      description: List of application segment IDs that were updated.
      type: list
      elements: str
      sample: ["216196257331372697", "216196257331372698"]
    match_style:
      description: The match_style that was applied.
      type: str
      sample: "INCLUSIVE"
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


def get_current_match_styles(client, application_ids, microtenant_id=None):
    """Fetch current match_style for each application segment."""
    match_styles = {}
    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    for app_id in application_ids:
        try:
            segment, _unused, error = client.application_segment.get_segment(
                app_id, query_params
            )
            if error:
                continue
            if segment:
                segment_dict = segment.as_dict() if hasattr(segment, "as_dict") else segment
                match_styles[app_id] = segment_dict.get("match_style", "")
        except Exception:
            continue

    return match_styles


def core(module):
    client = ZPAClientHelper(module)

    application_ids = module.params.get("application_ids")
    match_style = module.params.get("match_style")
    microtenant_id = module.params.get("microtenant_id")

    if not application_ids or len(application_ids) == 0:
        module.fail_json(msg="At least one application ID must be provided in 'application_ids'")

    # Convert application_ids to integers for the API
    try:
        application_ids_int = [int(app_id) for app_id in application_ids]
    except ValueError as e:
        module.fail_json(msg=f"Invalid application ID format: {to_native(e)}")

    # Check current state for drift detection
    current_match_styles = get_current_match_styles(client, application_ids, microtenant_id)

    # Determine if any update is needed
    needs_update = False
    for app_id in application_ids:
        current = current_match_styles.get(app_id, "")
        if current != match_style:
            needs_update = True
            break

    if module.check_mode:
        module.exit_json(changed=needs_update)

    if needs_update:
        # Build payload for bulk update
        kwargs = {
            "application_ids": application_ids_int,
            "match_style": match_style,
        }
        if microtenant_id:
            kwargs["microtenant_id"] = microtenant_id

        result, _unused, error = client.application_segment.bulk_update_multimatch(**kwargs)
        if error:
            module.fail_json(
                msg=f"Failed to bulk update multimatch: {to_native(error)}"
            )

        module.exit_json(
            changed=True,
            data={
                "message": "Bulk update multimatch operation completed successfully.",
                "application_ids": application_ids,
                "match_style": match_style,
            }
        )
    else:
        module.exit_json(
            changed=False,
            data={
                "message": "No changes required. All application segments already have the specified match_style.",
                "application_ids": application_ids,
                "match_style": match_style,
            }
        )


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        application_ids=dict(type="list", elements="str", required=True),
        match_style=dict(
            type="str",
            required=True,
            choices=["EXCLUSIVE", "INCLUSIVE"],
        ),
        microtenant_id=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()

