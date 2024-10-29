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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    connector = dict()
    params = [
        "id",
        "ids",  # Added ids param for bulk delete
        "name",
        "description",
        "enabled",
    ]
    for param_name in params:
        connector[param_name] = module.params.get(param_name, None)

    connector_id = connector.get("id", None)
    connector_name = connector.get("name", None)
    connector_ids = connector.get("ids", None)  # Get ids for bulk delete

    existing_connector = None

    # Handle single GET operation for retrieving an individual App Connector
    if connector_id is not None:
        connector_box = client.connectors.get_connector(connector_id=connector_id)
        if connector_box is not None:
            existing_connector = connector_box.to_dict()
    elif connector_name is not None:
        connectors = client.connectors.list_connectors().to_list()
        for connector_ in connectors:
            if connector_.get("name") == connector_name:
                existing_connector = connector_
                break

    if module.check_mode:
        if state == "present" and (existing_connector is None):
            module.exit_json(changed=True)
        elif state == "absent" and existing_connector is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    # Handle bulk delete operation independently from state
    if connector_ids:
        response = client.connectors.bulk_delete_connectors(connector_ids=connector_ids)
        module.exit_json(
            changed=True,
            data={"deleted_connectors": connector_ids, "response": response},
        )

    # Handle single delete operation when state is absent
    if state == "absent":
        if existing_connector and existing_connector.get("id"):
            code = client.connectors.delete_connector(
                connector_id=existing_connector.get("id")
            )
            if code > 299:
                module.fail_json(msg="Single delete failed", data=code)
            module.exit_json(changed=True, data=existing_connector)

    # Handle update if state is present (no creation logic)
    if state == "present":
        if existing_connector is not None:
            # Update existing connector
            update_required = False
            payload = {}

            # Check for differences and update only if necessary
            if module.params.get("description") is not None and module.params.get(
                "description"
            ) != existing_connector.get("description"):
                payload["description"] = module.params.get("description")
                update_required = True

            if module.params.get("enabled") is not None and module.params.get(
                "enabled"
            ) != existing_connector.get("enabled"):
                payload["enabled"] = module.params.get("enabled")
                update_required = True

            if module.params.get("name") is not None and module.params.get(
                "name"
            ) != existing_connector.get("name"):
                payload["name"] = module.params.get("name")
                update_required = True

            # Only send the update request if changes are detected
            if update_required:
                response = client.connectors.update_connector(
                    connector_id=existing_connector.get("id"), **payload
                )
                module.exit_json(changed=True, data=response.to_dict())
            else:
                # No update necessary, return existing data
                module.exit_json(changed=False, data=existing_connector)

    # Default exit
    module.exit_json(changed=False, data={})


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
