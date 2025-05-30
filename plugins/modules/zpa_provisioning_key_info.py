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
module: zpa_provisioning_key_info
short_description: Retrieves details about a Provisioning Key.
description:
  - This module will allow the retrieval of information abouta Provisioning Key by association type (CONNECTOR_GRP or SERVICE_EDGE_GRP).
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
    - Check mode is not supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
      - Name of the provisioning key.
    required: false
    type: str
  id:
    description:
      - ID of the provisioning key.
    required: false
    type: str
  key_type:
    type: str
    required: true
    choices: ["connector", "service_edge"]
    description:
      - "Specifies the provisioning key type for App Connectors or ZPA Private Service Edges."
      - "The supported values are CONNECTOR_GRP and SERVICE_EDGE_GRP."
"""

EXAMPLES = """
- name: Gather Details of All service_edge Provisioning Keys
  zscaler.zpacloud.zpa_provisioning_key_info:
    provider: "{{ zpa_cloud }}"
    key_type: "service_edge"

- name: Gather Details of All service_edge Provisioning Keys by Name
  zscaler.zpacloud.zpa_provisioning_key_info:
    provider: "{{ zpa_cloud }}"
    name: "Example Service Edge Group"
    key_type: "service_edge"

- name: Gather Details of All connector Provisioning Keys
  zscaler.zpacloud.zpa_provisioning_key_info:
    provider: "{{ zpa_cloud }}"
    key_type: "connector"

- name: Gather Details of All connector Provisioning Keys by Name
  zscaler.zpacloud.zpa_provisioning_key_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example Service Edge Group"
    key_type: "connector"
"""

RETURN = r"""
# ANY INFORMATION IN THIS DOCUMENT IS FOR EXAMPLE PURPOSES ONLY AND NOT USED IN PRODUCTION
provisioning_keys:
  description: Details of the provisioning keys that match the criteria.
  returned: always
  type: list
  elements: dict
  contains:
    creation_time:
      description: The time when the provisioning key was created, in epoch format.
      type: str
      sample: "1724115868"
    enabled:
      description: Indicates if the provisioning key is enabled.
      type: bool
      sample: true
    enrollment_cert_id:
      description: The ID of the associated enrollment certificate.
      type: str
      sample: "16560"
    enrollment_cert_name:
      description: The name of the associated enrollment certificate.
      type: str
      sample: "Connector"
    id:
      description: The unique identifier of the provisioning key.
      type: str
      sample: "38108"
    max_usage:
      description: The maximum number of times the provisioning key can be used.
      type: str
      sample: "10"
    modified_by:
      description: The ID of the user who last modified the provisioning key.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The time when the provisioning key was last modified, in epoch format.
      type: str
      sample: "1724115868"
    name:
      description: The name of the provisioning key.
      type: str
      sample: "Provisioning_Key01"
    provisioning_key:
      description: The actual provisioning key value.
      type: str
      sample: "3|api.private.zscaler.com|Befsgew"
    usage_count:
      description: The number of times the provisioning key has been used.
      type: str
      sample: "0"
    zcomponent_id:
      description: The ID of the associated component (App Connector Group or Service Edge Group).
      type: str
      sample: "216199618143441990"
    zcomponent_name:
      description: The name of the associated component (App Connector Group or Service Edge Group).
      type: str
      sample: "test_zpa_app_connector_group_2n8Cq"

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
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
    provisioning_key_id = module.params.get("id")
    provisioning_key_name = module.params.get("name")
    key_type = module.params.get("key_type")

    if not key_type:
        module.fail_json(
            msg="Parameter 'key_type' is required (e.g., 'connector' or 'service_edge')."
        )

    client = ZPAClientHelper(module)

    # Get provisioning key by ID
    if provisioning_key_id:
        result, _unused, error = client.provisioning.get_provisioning_key(
            key_id=provisioning_key_id, key_type=key_type
        )
        if error or not result:
            module.fail_json(
                msg=f"Failed to retrieve Provisioning Key ID: '{provisioning_key_id}'"
            )
        module.exit_json(
            changed=False,
            data=[result.as_dict() if hasattr(result, "as_dict") else result],
        )

    # Build query parameters for list
    query_params = {}
    if provisioning_key_name:
        query_params["search"] = provisioning_key_name

    # List provisioning keys
    module.warn(
        f"[Provisioning Key] Fetching keys of type '{key_type}' with params: {query_params}"
    )
    keys, err = collect_all_items(
        lambda qp: client.provisioning.list_provisioning_keys(
            key_type=key_type, query_params=qp
        ),
        query_params,
    )
    if err:
        module.fail_json(msg=f"Error retrieving provisioning keys: {to_native(err)}")

    module.warn(f"[Provisioning Key] Total keys retrieved: {len(keys)}")

    # Optional filtering by name after retrieval (case-sensitive exact match)
    if provisioning_key_name:
        filtered = [
            k for k in keys if getattr(k, "name", None) == provisioning_key_name
        ]
        if not filtered:
            available = [getattr(k, "name", None) for k in keys]
            module.fail_json(
                msg=f"Provisioning Key '{provisioning_key_name}' not found. Available: {available}"
            )
        keys = filtered

    result = [k.as_dict() if hasattr(k, "as_dict") else k for k in keys]
    module.exit_json(changed=False, provisioning_keys=result)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        key_type=dict(type="str", choices=["connector", "service_edge"], required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
