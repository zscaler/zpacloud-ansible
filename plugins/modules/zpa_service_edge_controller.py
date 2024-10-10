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
module: zpa_service_edge_controller
short_description: Manages Service Edge Controllers in the ZPA Cloud.
description:
  - This module Update/delete an Service Edge Controller in the ZPA Cloud.
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
      - The unique identifier of the Service Edge Controller.
    required: false
    type: str
  ids:
    description:
      - The unique identifiers of the bulk delete resources.
    required: false
    type: list
    elements: str
  name:
    description:
      - Name of the Service Edge Controller.
    required: false
    type: str
  description:
    description:
      - The description of the Service Edge Controller
    required: false
    type: str
  enabled:
    description:
      - Whether this Service Edge Controller is enabled or not.
    type: bool
"""

EXAMPLES = """
- name: Gather information about all Service Edges
  zscaler.zpacloud.zpa_service_edge_controller_info:
  register: result

- name: Extract Service Edge Controller IDs
  set_fact:
    service_edge_ids: "{{ result.pses | map(attribute='id') | list }}"

- name: Bulk delete Service Edge Controllers
  zscaler.zpacloud.zpa_service_edge_controller:
    ids: "{{ service_edge_ids }}"

- name: Update Service Edge Controller Description
  zscaler.zpacloud.zpa_service_edge_controller:
    name: 'ServiceEdgeController01'
    description: 'Update Service Edge Controller 01'
  register: result
"""

RETURN = """
# Default return values
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    pse = dict()
    params = [
        "id",
        "ids",  # Added ids param for bulk delete
        "name",
        "description",
        "enabled",
    ]
    for param_name in params:
        pse[param_name] = module.params.get(param_name, None)

    service_edge_id = pse.get("id", None)
    service_edge_name = pse.get("name", None)
    service_edge_ids = pse.get("ids", None)  # Get ids for bulk delete

    existing_pse = None

    # Handle single GET operation for retrieving an individual Service Edges
    if service_edge_id is not None:
        pse_box = client.service_edges.get_service_edge(service_edge_id=service_edge_id)
        if pse_box is not None:
            existing_pse = pse_box.to_dict()
    elif service_edge_name is not None:
        pses = client.service_edges.list_service_edges().to_list()
        for pse_ in pses:
            if pse_.get("name") == service_edge_name:
                existing_pse = pse_
                break

    if module.check_mode:
        if state == "present" and (existing_pse is None):
            module.exit_json(changed=True)
        elif state == "absent" and existing_pse is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    # Handle bulk delete operation independently from state
    if service_edge_ids:
        response = client.service_edges.bulk_delete_service_edges(
            service_edge_ids=service_edge_ids
        )
        module.exit_json(
            changed=True, data={"deleted_pses": service_edge_ids, "response": response}
        )

    # Handle single delete operation when state is absent
    if state == "absent":
        if existing_pse and existing_pse.get("id"):
            code = client.service_edges.delete_service_edge(
                service_edge_id=existing_pse.get("id")
            )
            if code > 299:
                module.fail_json(msg="Single delete failed", data=code)
            module.exit_json(changed=True, data=existing_pse)

    # Handle create or update if state is present
    if state == "present":
        if existing_pse is not None:
            # Update existing connector
            update_required = False
            payload = {}

            # Check for differences and update only if necessary
            if module.params.get("description") is not None and module.params.get(
                "description"
            ) != existing_pse.get("description"):
                payload["description"] = module.params.get("description")
                update_required = True

            if module.params.get("enabled") is not None and module.params.get(
                "enabled"
            ) != existing_pse.get("enabled"):
                payload["enabled"] = module.params.get("enabled")
                update_required = True

            if module.params.get("name") is not None and module.params.get(
                "name"
            ) != existing_pse.get("name"):
                payload["name"] = module.params.get("name")
                update_required = True

            # Only send the update request if changes are detected
            if update_required:
                response = client.service_edges.update_service_edge(
                    service_edge_id=existing_pse.get("id"), **payload
                )
                module.exit_json(changed=True, data=response.to_dict())
            else:
                # No update necessary, return existing data
                module.exit_json(changed=False, data=existing_pse)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        ids=dict(
            type="list", elements="str", required=False
        ),
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
