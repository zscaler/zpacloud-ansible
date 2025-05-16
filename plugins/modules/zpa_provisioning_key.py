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
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    collect_all_items,
)


def normalize_provisioning_key(prov_key):
    """
    Normalize provisioning key data by setting computed values.
    """
    normalized = prov_key.copy()
    computed_values = [
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

    # If the API returns 'maxUsage', map it to 'max_usage'
    if "maxUsage" in normalized:
        normalized["max_usage"] = normalized.pop("maxUsage")

    # Convert 'max_usage' string to int if present (avoid drift "10" vs 10)
    if "max_usage" in normalized and normalized["max_usage"] is not None:
        try:
            normalized["max_usage"] = int(normalized["max_usage"])
        except ValueError:
            # If there's some unexpected string that can't convert to int, fail or just skip
            pass

    # If the API still returns 'zcomponent_id', rename it to 'component_id'
    if "zcomponent_id" in normalized:
        normalized["component_id"] = normalized.pop("zcomponent_id")

    # Remove `key_type` since it's only for URL construction and not part of the API data
    normalized.pop("key_type", None)

    return normalized


def fetch_enrollment_cert_id(module, client, key_type):
    """
    Fetch the enrollment certificate ID based on association type (connector vs service_edge).
    The returned ID is then used as 'enrollment_cert_id'.
    """
    # We simply pass {"type": key_type} as query_params
    query_params = {"type": key_type}

    # This matches the same pattern as your info resource
    cert_list, err = collect_all_items(
        client.enrollment_certificates.list_enrolment, query_params
    )
    if err:
        module.fail_json(
            msg=f"Error retrieving Enrollment Certificates: {to_native(err)}"
        )

    result_list = [g.as_dict() for g in cert_list]
    if not result_list:
        return None

    # For simplicity, just take the first certificate ID
    return result_list[0].get("id")


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    provisioning_key_dict = dict()
    key_type = module.params.get("key_type")

    # Fetch and set the enrollment certificate ID
    module.warn("Fetching enrollment certificate ID based on key_type")
    enrollment_cert_id = fetch_enrollment_cert_id(module, client, key_type)
    if not enrollment_cert_id:
        module.fail_json(msg=f"Enrollment certificate for {key_type} not found.")

    params = [
        "id",
        "microtenant_id",
        "name",
        "enabled",
        "max_usage",
        "enrollment_cert_id",
        "component_id",
        "key_type",
    ]

    for param_name in params:
        provisioning_key_dict[param_name] = module.params.get(param_name, None)

    provisioning_key_dict["enrollment_cert_id"] = enrollment_cert_id
    module.warn(f"Provisioning key parameters initialized: {provisioning_key_dict}")

    key_id = provisioning_key_dict.get("id")
    key_name = provisioning_key_dict.get("name")
    microtenant_id = provisioning_key_dict.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_key = None

    if key_id is not None:
        # Fetch by ID if provided
        result, _, error = client.provisioning.get_provisioning_key(
            key_id,
            key_type,
            query_params={"microtenant_id": microtenant_id},
        )
        if error:
            module.fail_json(
                msg=f"Error fetching provisioning key with id {key_id}: {to_native(error)}"
            )
        existing_key = result.as_dict()
    else:
        # We define a wrapper function to match your existing info resource style
        def list_prov_keys(local_query_params=None):
            return client.provisioning.list_provisioning_keys(
                key_type, local_query_params
            )

        # Now call collect_all_items() with two args: the wrapper + query_params
        result, error = collect_all_items(list_prov_keys, query_params)
        if error:
            module.fail_json(msg=f"Error provisioning keys: {to_native(error)}")
        if result:
            for group_ in result:
                if group_.name == key_name:
                    existing_key = group_.as_dict()
                    break

    # Debugging: Display the current state (what Ansible sees from the API)
    module.warn(f"Current provisioning key from API: {existing_key}")

    desired_key = normalize_provisioning_key(provisioning_key_dict)
    current_key = normalize_provisioning_key(existing_key) if existing_key else {}

    # Debugging: Show normalized values for comparison
    module.warn(f"Normalized Desired: {desired_key}")
    module.warn(f"Normalized Current: {current_key}")

    fields_to_exclude = ["id"]
    differences_detected = False
    for k, v in desired_key.items():
        module.warn(f"Comparing key: {k}, Desired: {v}, Current: {current_key.get(k)}")
        if k not in fields_to_exclude and current_key.get(k) != v:
            differences_detected = True
            module.warn(
                f"Difference detected in {k}. Current: {current_key.get(k)}, Desired: {v}"
            )

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
        if differences_detected and existing_key:
            # Update the existing provisioning key if differences are found
            update_key = deleteNone(
                {
                    "key_id": existing_key.get("id"),
                    "microtenant_id": desired_key.get("microtenant_id", None),
                    "name": desired_key["name"],
                    "enabled": desired_key.get("enabled"),
                    "max_usage": desired_key.get("max_usage"),
                    "enrollment_cert_id": desired_key.get("enrollment_cert_id"),
                    "component_id": desired_key.get("component_id"),
                    "key_type": desired_key.get("key_type"),
                }
            )
            module.warn(f"Payload Update for SDK: {update_key}")
            updated_key, _, error = client.provisioning.update_provisioning_key(
                group_id=update_key.pop("key_id"), key_type=key_type, **update_key
            )
            if error:
                module.fail_json(
                    msg=f"Error updating provisioning key: {to_native(error)}"
                )
            module.exit_json(changed=True, data=updated_key.as_dict())

        elif not existing_key:
            # Create
            create_key = deleteNone(
                {
                    "microtenant_id": desired_key.get("microtenant_id", None),
                    "name": desired_key["name"],
                    "enabled": desired_key.get("enabled"),
                    "max_usage": desired_key.get("max_usage"),
                    "enrollment_cert_id": desired_key.get("enrollment_cert_id"),
                    "component_id": desired_key.get("component_id"),
                    "key_type": desired_key.get("key_type"),
                }
            )
            module.warn("Payload Update for SDK: {}".format(create_key))
            created, _, error = client.provisioning.add_provisioning_key(
                key_type, **create_key
            )
            if error:
                module.fail_json(
                    msg=f"Error creating provisioning key: {to_native(error)}"
                )
            module.exit_json(changed=True, data=created.as_dict())
        else:
            # No changes needed
            module.exit_json(changed=False, data=existing_key)

    elif state == "absent":
        if existing_key:
            _, _, error = client.provisioning.delete_provisioning_key(
                group_id=existing_key.get("id"),
                key_type=key_type,
                microtenant_id=microtenant_id,
            )
            if error:
                module.fail_json(
                    msg=f"Error deleting provisioning key: {to_native(error)}"
                )
            module.exit_json(changed=True, data=existing_key)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = dict(
        key_type=dict(type="str", required=True, choices=["connector", "service_edge"]),
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        enabled=dict(type="bool", required=False, default=True),
        max_usage=dict(type="int", required=True),
        enrollment_cert_id=dict(type="str", required=False),
        component_id=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
