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


def normalize_provisioning_key(prov_key):
    """
    Normalize provisioning key data by setting computed values.
    """
    normalized = prov_key.copy()
    computed_values = [
        "id",
        "creation_time",
        "modified_by",
        "modified_time",
        "enrollment_cert_name",
        "provisioning_key",
        "zcomponent_name",
        "usage_count",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    # Map 'zcomponent_id' to 'component_id' for consistency
    if "zcomponent_id" in normalized:
        normalized["component_id"] = normalized.pop("zcomponent_id")

    # Remove `key_type` since it's only for URL construction and not part of the API data
    normalized.pop("key_type", None)

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
    module.warn("Fetching enrollment certificate ID based on key_type")
    enrollment_cert_id = fetch_enrollment_cert_id(client, key_type)
    if not enrollment_cert_id:
        module.fail_json(msg=f"Enrollment certificate for {key_type} not found.")
    # module.warn(f"Enrollment certificate ID fetched: {enrollment_cert_id}")

    provisioning_key = {
        param: module.params.get(param)
        for param in [
            "id",
            "name",
            "enabled",
            "max_usage",
            "enrollment_cert_id",
            "component_id",
            "key_type",
        ]
    }
    provisioning_key["enrollment_cert_id"] = enrollment_cert_id
    # module.warn(f"Provisioning key parameters initialized: {provisioning_key}")

    existing_key = None
    if provisioning_key["id"]:
        # Fetch by ID if ID is provided
        # module.warn(f"Fetching existing key by ID: {provisioning_key['id']}")
        existing_key = client.provisioning.get_provisioning_key(
            key_id=provisioning_key["id"], key_type=key_type
        )
    else:
        # Fetch by name if ID is not provided
        # module.warn(f"Fetching existing keys by name: {provisioning_key['name']}")
        keys = client.provisioning.list_provisioning_keys(key_type=key_type).to_list()
        for k in keys:
            if k.get("name") == provisioning_key["name"]:
                existing_key = k
                break
    module.warn(f"Existing key found: {existing_key}")

    if existing_key:
        # Normalize and compare existing key to see if an update is needed
        desired_key = normalize_provisioning_key(provisioning_key)
        current_key = normalize_provisioning_key(existing_key)
        module.warn(f"Normalized desired key: {desired_key}")
        module.warn(f"Normalized current key: {current_key}")

        # Fields to exclude from comparison, such as IDs and auto-generated values
        fields_to_exclude = ["id", "key_type", "provisioning_key"]

        # Check for actual differences, excluding fields with None in desired_key
        differences_detected = any(
            desired_key.get(key) is not None and desired_key.get(key) != current_key.get(key)
            for key in desired_key
            if key not in fields_to_exclude
        )

        # module.warn(f"Differences detected: {differences_detected}")

        if module.check_mode:
            # If in check mode, report changes and exit
            module.warn("Running in check mode")
            if state == "present" and (existing_key is None or differences_detected):
                module.exit_json(changed=True)
            elif state == "absent" and existing_key is not None:
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False)

        if state == "present":
            if differences_detected:
                # Update the existing provisioning key if differences are found
                update_payload = deleteNone(
                    dict(
                        key_id=existing_key.get("id"),
                        name=provisioning_key["name"],
                        enabled=provisioning_key.get("enabled"),
                        max_usage=provisioning_key.get("max_usage"),
                        enrollment_cert_id=provisioning_key.get("enrollment_cert_id"),
                        component_id=provisioning_key.get("component_id"),
                        key_type=provisioning_key.get("key_type"),
                    )
                )
                # module.warn(f"Update payload: {update_payload}")
                updated_key = client.provisioning.update_provisioning_key(
                    **update_payload
                )
                # module.warn(f"Response from update: {updated_key}")
                module.exit_json(changed=True, data=updated_key)
            else:
                # No update required
                # module.warn("No update required; exiting without changes")
                module.exit_json(changed=False, data=existing_key)

        elif state == "absent":
            # Delete the existing provisioning key
            # module.warn(f"Deleting provisioning key with ID: {existing_key['id']}")
            delete_code = client.provisioning.delete_provisioning_key(
                key_id=existing_key["id"], key_type=key_type
            )
            # module.warn(f"Response code from delete: {delete_code}")
            if delete_code > 299:
                module.fail_json(msg="Failed to delete the provisioning key", code=delete_code)
            module.exit_json(changed=True, data=existing_key)

    elif state == "present":
        # Create a new provisioning key if it does not exist
        create_payload = deleteNone(
            dict(
                name=provisioning_key["name"],
                enabled=provisioning_key["enabled"],
                max_usage=provisioning_key["max_usage"],
                enrollment_cert_id=provisioning_key["enrollment_cert_id"],
                component_id=provisioning_key["component_id"],
                key_type=provisioning_key["key_type"],
            )
        )
        # module.warn(f"Create payload: {create_payload}")
        new_key = client.provisioning.add_provisioning_key(**create_payload).to_dict()
        module.warn(f"Response from create: {new_key}")
        module.exit_json(changed=True, data=new_key)

    elif state == "absent" and not existing_key:
        # No action needed if resource does not exist and state is absent
        # module.warn("No existing key to delete; exiting without changes")
        module.exit_json(changed=False)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        enabled=dict(type="bool", required=False),
        max_usage=dict(type="str", required=True),
        component_id=dict(type="str", required=True),
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
