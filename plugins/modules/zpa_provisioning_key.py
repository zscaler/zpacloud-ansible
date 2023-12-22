#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
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
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
  - zscaler.zpacloud.fragments.state
options:
  enabled:
    description: ""
    type: bool
    default: True
    required: False
  id:
    description: ""
    type: str
    required: False
  max_usage:
    description: ""
    type: str
    required: True
  name:
    description: ""
    type: str
    required: True
  provisioning_key:
    description: ""
    type: str
    required: False
  enrollment_cert_id:
    description: ""
    type: str
    required: True
  usage_count:
    description: ""
    type: str
    required: False
  zcomponent_id:
    description: ""
    type: str
    required: True
  association_type:
    description: ""
    type: str
    choices: ['connector', 'service_edge']
    required: True
"""

EXAMPLES = """
- name: Get ID Information of a Connector Enrollment Certificate
  zscaler.zpacloud.zpa_enrollement_certificate_facts:
    provider: "{{ zpa_cloud }}"
    name: "Connector"
  register: enrollment_cert_connector

- name: Get ID Information of a App Connector Group
  zscaler.zpacloud.zpa_app_connector_groups_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example"
  register: app_connector_group

- name: "Create/Update/Delete App Connector Group Provisioning Key"
  zscaler.zpacloud.zpa_provisioning_key:
    provider: "{{ zpa_cloud }}"
    name: "App Connector Group Provisioning Key"
    association_type: "connector"
    max_usage: "10"
    enrollment_cert_id: "{{ enrollment_cert_connector.data[0].id }}"
    zcomponent_id: "{{ enrollment_cert_connector.data[0].id }}"
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
        "creation_time",
        "modified_by",
        "modified_time",
        "association_type",
        "usage_count",
        "max_usage",
        "enrollment_cert_id",
        "zcomponent_id",
        "enabled",
    ]
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    provisioning_key = dict()
    params = [
        "enabled",
        "id",
        "max_usage",
        "name",
        "provisioning_key",
        "enrollment_cert_id",
        "usage_count",
        "zcomponent_id",
        "association_type",
    ]
    for param_name in params:
        provisioning_key[param_name] = module.params.get(param_name, None)
    provisioning_key_id = module.params.get("id", None)
    provisioning_key_name = module.params.get("name", None)
    association_type = module.params.get("association_type")
    existing_key = None
    if provisioning_key_id is not None:
        existing_key = client.provisioning.get_provisioning_key(
            key_id=provisioning_key_id, key_type=association_type
        )
    elif provisioning_key_name is not None:
        keys = client.provisioning.list_provisioning_keys(
            key_type=association_type
        ).to_list()
        for k in keys:
            if k.get("name") == provisioning_key_name:
                existing_key = k
                break

    # Normalize and compare existing and desired application data
    normalized_key = normalize_provisioning_key(provisioning_key)
    normalized_existing_key = (
        normalize_provisioning_key(existing_key) if existing_key else {}
    )

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in normalized_key.items():
        if key not in fields_to_exclude and normalized_existing_key.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {normalized_existing_key.get(key)}, Desired: {value}"
            )

    if existing_key is not None:
        id = existing_key.get("id")
        existing_key.update(provisioning_key)
        existing_key["id"] = id

    if state == "present":
        if existing_key is not None:
            if differences_detected:
                """Update"""
                existing_key = deleteNone(
                    dict(
                        key_id=existing_key.get("id", None),
                        key_type=association_type,
                        name=existing_key.get("name", None),
                        max_usage=existing_key.get("max_usage", None),
                        enrollment_cert_id=existing_key.get("enrollment_cert_id", None),
                        component_id=existing_key.get("zcomponent_id", None),
                        provisioning_key=existing_key.get("provisioning_key", None),
                    )
                )
                existing_key = client.provisioning.update_provisioning_key(
                    **existing_key
                )
                module.exit_json(changed=True, data=existing_key)
            else:
                """No Changes Needed"""
                module.exit_json(changed=False, data=existing_key)
        else:
            """Create"""
            provisioning_key = deleteNone(
                dict(
                    key_type=association_type,
                    name=provisioning_key.get("name", None),
                    enabled=provisioning_key.get("enabled", None),
                    max_usage=provisioning_key.get("max_usage", None),
                    enrollment_cert_id=provisioning_key.get("enrollment_cert_id", None),
                    component_id=provisioning_key.get("zcomponent_id", None),
                    provisioning_key=provisioning_key.get("provisioning_key", None),
                )
            )
            provisioning_key = client.provisioning.add_provisioning_key(
                **provisioning_key
            )
            module.exit_json(changed=False, data=provisioning_key)
    elif state == "absent" and existing_key is not None:
        client.provisioning.delete_provisioning_key(
            key_id=existing_key.get("id"), key_type=association_type
        )
        module.exit_json(changed=False, data=existing_key)
    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        enabled=dict(type="bool", default=True, required=False),
        id=dict(type="str", required=False),
        max_usage=dict(type="str", required=False),
        name=dict(type="str", required=True),
        provisioning_key=dict(
            type="str",
            required=False,
        ),
        enrollment_cert_id=dict(type="str", required=False),
        usage_count=dict(type="str", required=False),
        zcomponent_id=dict(type="str", required=False),
        association_type=dict(
            type="str",
            choices=["CONNECTOR_GRP", "connector", "service_edge", "SERVICE_EDGE_GRP"],
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
