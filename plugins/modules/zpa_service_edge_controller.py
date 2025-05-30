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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Extract parameters
    params = ["id", "ids", "name", "description", "enabled", "microtenant_id"]
    service_edge = {p: module.params.get(p) for p in params}
    service_edge_id = service_edge.get("id")
    service_edge_ids = service_edge.get("ids") or []
    service_edge_name = service_edge.get("name")
    microtenant_id = service_edge.get("microtenant_id")

    # Step 1: Handle bulk delete (skips state)
    if service_edge_ids:
        _unused, _unused, error = client.service_edges.bulk_delete_service_edges(
            service_edge_ids=service_edge_ids, microtenant_id=microtenant_id
        )
        if error:
            module.fail_json(msg=f"Error during bulk delete: {to_native(error)}")
        module.exit_json(changed=True, data={"deleted_service_edges": service_edge_ids})

    # Step 2: Lookup existing service_edge by ID or name
    existing_service_edge = None
    if service_edge_id:
        result, _unused, error = client.service_edges.get_service_edge(
            service_edge_id=service_edge_id,
            query_params={"microtenant_id": microtenant_id} if microtenant_id else {},
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving service edge by ID: {to_native(error)}"
            )
        if result:
            existing_service_edge = result.as_dict()
    elif service_edge_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        connectors, error = collect_all_items(
            client.service_edges.list_service_edges, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing service edges: {to_native(error)}")
        for pse in connectors or []:
            pse_dict = pse.as_dict()
            if pse_dict.get("name") == service_edge_name:
                existing_service_edge = pse_dict
                break

    # Step 3: Check mode support
    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and not existing_service_edge)
            or (state == "absent" and existing_service_edge is not None)
        )

    # Step 4: Delete
    if state == "absent" and existing_service_edge:
        _unused, _unused, error = client.service_edges.delete_connector(
            service_edge_id=existing_service_edge.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting service edge: {to_native(error)}")
        module.exit_json(changed=True, data=existing_service_edge)

    # Step 5: Update (no creation support per spec)
    if state == "present" and existing_service_edge:
        payload = {}
        update_required = False

        for key in ["name", "description", "enabled"]:
            if pse.get(key) is not None and pse.get(key) != existing_service_edge.get(
                key
            ):
                payload[key] = pse[key]
                update_required = True

        if update_required:
            payload["microtenant_id"] = microtenant_id
            updated, _unused, error = client.service_edges.update_service_edge(
                service_edge_id=existing_service_edge.get("id"), **payload
            )
            if error:
                module.fail_json(msg=f"Error updating service edge: {to_native(error)}")
            module.exit_json(changed=True, data=updated.as_dict())

        # No update needed
        module.exit_json(changed=False, data=existing_service_edge)

    # Final fallback
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        ids=dict(type="list", elements="str", required=False),
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        microtenant_id=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        ids=dict(type="list", elements="str", required=False),
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
