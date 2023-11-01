#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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
module: zpa_provisioning_key_facts
short_description: Retrieves details about a Provisioning Key.
description:
  - This module will allow the retrieval of information abouta Provisioning Key by association type (CONNECTOR_GRP or SERVICE_EDGE_GRP).
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
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
  association_type:
    type: str
    required: true
    choices: ["CONNECTOR_GRP", "SERVICE_EDGE_GRP"]
    description:
      - "Specifies the provisioning key type for App Connectors or ZPA Private Service Edges."
      - "The supported values are CONNECTOR_GRP and SERVICE_EDGE_GRP."
"""

EXAMPLES = """
- name: Gather Details of All SERVICE_EDGE_GRP Provisioning Keys
  zscaler.zpacloud.zpa_provisioning_key_facts:
    provider: "{{ zpa_cloud }}"
    association_type: "SERVICE_EDGE_GRP"

- name: Gather Details of All SERVICE_EDGE_GRP Provisioning Keys by Name
  zscaler.zpacloud.zpa_provisioning_key_facts:
    provider: "{{ zpa_cloud }}"
    name: "Example Service Edge Group"
    association_type: "SERVICE_EDGE_GRP"

- name: Gather Details of All SERVICE_EDGE_GRP Provisioning Keys by ID
  zscaler.zpacloud.zpa_provisioning_key_facts:
    provider: "{{ zpa_cloud }}"
    id: "8691"
    association_type: "SERVICE_EDGE_GRP"
"""

RETURN = """
# Returns information on a specified provisioning key resource.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule


def core(module):
    provisioning_key_id = module.params.get("id", None)
    provisioning_key_name = module.params.get("name", None)
    association_type = module.params.get("association_type", None)
    client = ZPAClientHelper(module)
    keys = []
    if provisioning_key_id is not None:
        key_box = client.provisioning.get_provisioning_key(
            key_id=provisioning_key_id, key_type=association_type
        )
        if key_box is None:
            module.fail_json(
                msg="Failed to retrieve App Connector ID: '%s'" % (provisioning_key_id)
            )
        keys = [key_box.to_dict()]
    else:
        keys = client.provisioning.list_provisioning_keys(
            key_type=association_type
        ).to_list()
        if provisioning_key_name is not None:
            key_found = False
            for key in keys:
                if key.get("name") == provisioning_key_name:
                    key_found = True
                    keys = [key]
            if not key_found:
                module.fail_json(
                    msg="Failed to retrieve App Connector Name: '%s'"
                    % (provisioning_key_name)
                )
    module.exit_json(changed=False, data=keys)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        association_type=dict(
            type="str", choices=["connector", "service_edge"], required=True
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
