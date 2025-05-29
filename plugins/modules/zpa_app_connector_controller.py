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
module: zpa_app_connector_controller
short_description: Manages App Connector Controllers in the ZPA Cloud.
description:
  - This module Update/delete an App Connector Controller in the ZPA Cloud.
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
      - The unique identifier of the App Connector.
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
      - Name of the App Connector.
    required: false
    type: str
  description:
    description:
      - The description of the App Connector.
    required: false
    type: str
  enabled:
    description:
      - Whether this App Connector is enabled or not.
    type: bool
"""

EXAMPLES = """
- name: Gather information about all App Connector Controllers
  zscaler.zpacloud.zpa_app_connector_controller_info:
  register: result

- name: Extract App Connector IDs
  set_fact:
    app_connector_ids: "{{ result.connectors | map(attribute='id') | list }}"

- name: Bulk delete App Connector Controllers
  zscaler.zpacloud.zpa_app_connector_controller:
    ids: "{{ app_connector_ids }}"

- name: Update Service Edge Controller Description
  zscaler.zpacloud.zpa_app_connector_controller:
    name: 'AppConnectorController01'
    description: 'Update App Connector Controller 01'
  register: result
"""

RETURN = """
# Default return values
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Extract parameters
    params = ["id", "ids", "name", "description", "enabled", "microtenant_id"]
    connector = {p: module.params.get(p) for p in params}
    connector_id = connector.get("id")
    connector_ids = connector.get("ids") or []
    connector_name = connector.get("name")
    microtenant_id = connector.get("microtenant_id")

    # Step 1: Handle bulk delete (skips state)
    if connector_ids:
        _unused, _unused, error = client.app_connectors.bulk_delete_connectors(
            connector_ids=connector_ids, microtenant_id=microtenant_id
        )
        if error:
            module.fail_json(msg=f"Error during bulk delete: {to_native(error)}")
        module.exit_json(changed=True, data={"deleted_connectors": connector_ids})

    # Step 2: Lookup existing connector by ID or name
    existing_connector = None
    if connector_id:
        result, _unused, error = client.app_connectors.get_connector(
            connector_id=connector_id,
            query_params={"microtenant_id": microtenant_id} if microtenant_id else {},
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving connector by ID: {to_native(error)}"
            )
        if result:
            existing_connector = result.as_dict()
    elif connector_name:
        query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}
        connectors, error = collect_all_items(
            client.app_connectors.list_connectors, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing connectors: {to_native(error)}")
        for conn in connectors or []:
            conn_dict = conn.as_dict()
            if conn_dict.get("name") == connector_name:
                existing_connector = conn_dict
                break

    # Step 3: Check mode support
    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and not existing_connector)
            or (state == "absent" and existing_connector is not None)
        )

    # Step 4: Delete
    if state == "absent" and existing_connector:
        _unused, _unused, error = client.app_connectors.delete_connector(
            connector_id=existing_connector.get("id"),
            microtenant_id=microtenant_id,
        )
        if error:
            module.fail_json(msg=f"Error deleting connector: {to_native(error)}")
        module.exit_json(changed=True, data=existing_connector)

    # Step 5: Update (no creation support per spec)
    if state == "present" and existing_connector:
        payload = {}
        update_required = False

        for key in ["name", "description", "enabled"]:
            if connector.get(key) is not None and connector.get(
                key
            ) != existing_connector.get(key):
                payload[key] = connector[key]
                update_required = True

        if update_required:
            payload["microtenant_id"] = microtenant_id
            updated, _unused, error = client.app_connectors.update_connector(
                connector_id=existing_connector.get("id"), **payload
            )
            if error:
                module.fail_json(msg=f"Error updating connector: {to_native(error)}")
            module.exit_json(changed=True, data=updated.as_dict())

        # No update needed
        module.exit_json(changed=False, data=existing_connector)

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
