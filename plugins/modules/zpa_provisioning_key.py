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
module: zpa_provisioning_key
short_description: Create a Provisioning Key.
description:
  - This module will create/update/delete a specific Provisioning Key by association type (CONNECTOR_GRP or SERVICE_EDGE_GRP).
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
    description: "The unique identifier of the provisioning key"
    type: str
    required: false
  name:
    description: "The name of the provisioning key"
    type: str
    required: true
  enabled:
    description: "Whether or not this provisioning key is enabled"
    type: bool
    required: false
  max_usage:
    description: "The maximum usage of the provisioning key"
    type: str
    required: true
  component_id:
    description: "The unique identifier of the App Connector or Service Edge"
    type: str
    required: true
  key_type:
    description:
      - Specifies the provisioning key type for App Connectors or ZPA Private Service Edges.
      - The supported values are CONNECTOR_GRP (App Connector group) and SERVICE_EDGE_GRP (ZPA Private Service Edge group).
    type: str
    choices: ['connector', 'service_edge']
    required: true
"""

EXAMPLES = """
- name: Get ID Information of a Connector Enrollment Certificate
  zscaler.zpacloud.zpa_enrollement_certificate_Info:
    provider: "{{ zpa_cloud }}"
    name: "Connector"
  register: enrollment_cert_connector

- name: Get ID Information of a App Connector Group
  zscaler.zpacloud.zpa_app_connector_group_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example"
  register: app_connector_group

- name: "Create/Update/Delete App Connector Group Provisioning Key"
  zscaler.zpacloud.zpa_provisioning_key:
    provider: "{{ zpa_cloud }}"
    name: "App Connector Group Provisioning Key"
    key_type: "connector"
    max_usage: "10"
    enrollment_cert_id: "{{ enrollment_cert_connector.data[0].id }}"
    component_id: "{{ enrollment_cert_connector.data[0].id }}"
"""

RETURN = """
# The newly created app connector group or service edge group provisioning key resource record.
"""

from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import deleteNone
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_provisioning_key(group):
    """
    Normalize provisioning key data by setting computed values.
    """
    normalized = group.copy()
    computed_values = [
      "id",
      "creation_time",
      "modified_by",
      "modified_time",
      "enrollment_cert_name",
      "provisioning_key",
      "zcomponent_name"
      "usage_count",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    # Map 'zcomponent_id' to 'component_id' for consistency
    if 'zcomponent_id' in normalized:
        normalized['component_id'] = normalized.pop('zcomponent_id')

    # Remove `key_type` since it's only for URL construction and not part of the API data
    normalized.pop('key_type', None)

    return normalized


def fetch_enrollment_cert_id(client, key_type):
    """
    Fetch the enrollment certificate ID based on association type.
    """
    cert_name = "Connector" if key_type == "connector" else "Service Edge"
    cert = client.certificates.get_enrolment_cert_by_name(cert_name)
    return cert.get("id") if cert else None


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    key_type = module.params.get("key_type")

    # Fetch and set the enrollment certificate ID
    enrollment_cert_id = fetch_enrollment_cert_id(client, key_type)
    if not enrollment_cert_id:
        module.fail_json(msg=f"Enrollment certificate for {key_type} not found.")

    provisioning_key = {
        param: module.params.get(param)
        for param in [
            "id",
            "name",
            "enabled",
            "max_usage",
            "enrollment_cert_id",
            "component_id",  # The user-facing attribute
            "key_type",
            "provisioning_key",
        ]
    }
    provisioning_key["enrollment_cert_id"] = enrollment_cert_id  # Set the fetched ID
    provisioning_key_id = module.params.get("id", None)

    # Debugging: Display the desired state
    # module.warn(f"Desired provisioning key: {provisioning_key}")

    existing_key = None
    if provisioning_key_id is not None:
        existing_key = client.provisioning.get_provisioning_key(
            key_id=provisioning_key_id, key_type=key_type
        )
    else:
        keys = client.provisioning.list_provisioning_keys(key_type=key_type).to_list()
        for k in keys:
            if k.get("name") == module.params.get("name"):
                existing_key = k
                break

    # Debugging: Display the current state (what Ansible sees from the API)
    # module.warn(f"Current provisioning key from API: {existing_key}")

    # Set defaults for desired state to avoid drift due to None values
    if provisioning_key.get('enabled') is None:
        provisioning_key['enabled'] = True  # Set to True if not explicitly set

    desired_key = normalize_provisioning_key(provisioning_key)
    current_key = normalize_provisioning_key(existing_key) if existing_key else {}

    # Handle the component_id/zcomponent_id mapping during comparison only
    if 'zcomponent_id' in current_key:
        current_key['component_id'] = current_key.pop('zcomponent_id')

    # Debugging: Show normalized values for comparison
    # module.warn(f"Normalized Desired: {desired_key}")
    # module.warn(f"Normalized Current: {current_key}")

    fields_to_exclude = ["id", "key_type"]
    differences_detected = False
    for key, value in desired_key.items():
        # Debugging: Track comparisons for each key-value pair
        # module.warn(f"Comparing key: {key}, Desired: {value}, Current: {current_key.get(key)}")

        if key not in fields_to_exclude and current_key.get(key) != value:
            differences_detected = True
            # module.warn(f"Difference detected in {key}. Current: {current_key.get(key)}, Desired: {value}")

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_key is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_key is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_key is not None and differences_detected:
        # Ensure 'key_type' is not passed twice
        update_params = deleteNone(provisioning_key)
        update_params.pop("key_type", None)  # Remove key_type to prevent duplication

        # module.warn(f"Final payload being sent to SDK: {provisioning_key}")
        existing_key = client.provisioning.update_provisioning_key(
            key_id=existing_key.get("id"),  # Passing key_id directly
            key_type=key_type,  # Passing key_type directly
            **update_params,
        )
        module.exit_json(changed=True, data=existing_key)

    elif not existing_key:
        new_key = client.provisioning.add_provisioning_key(
            **deleteNone(provisioning_key)
        )
        module.exit_json(changed=True, data=new_key)
    else:
        module.exit_json(changed=False, data=existing_key)

    if state == "absent":
        client.provisioning.delete_provisioning_key(
            key_id=provisioning_key_id, key_type=key_type
        )
        module.exit_json(changed=True)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        enabled=dict(type="bool", required=False),
        max_usage=dict(type="str", required=True),
        component_id=dict(type="str", required=True),
        provisioning_key=dict(type="str", required=False),
        key_type=dict(type="str", choices=["connector", "service_edge"], required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
