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

module: zpa_trusted_networks_facts
short_description: Retrieves information about a Trusted Network.
description:
    - This module will allow the retrieval of information about Trusted Network resource.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.credentials_set
options:
    id:
        description:
            - ID of the trusted network.
        required: false
        type: str
    name:
        description:
            - Name of the trusted network.
        required: false
        type: str
"""

EXAMPLES = """
- name: Get Information About All Trusted Networks
  zscaler.zpacloud.zpa_trusted_networks_facts:
    provider: "{{ zpa_cloud }}"

- name: Get information about Trusted Networks by Name
  zscaler.zpacloud.zpa_trusted_networks_facts:
    provider: "{{ zpa_cloud }}"
    name: Corp-Trusted-Networks

- name: Get information about Trusted Networks by ID
  zscaler.zpacloud.zpa_trusted_networks_facts:
    provider: "{{ zpa_cloud }}"
    id: 216196257331282234
"""

RETURN = """
# Returns information on a specified Trusted Network.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    remove_cloud_suffix,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    network_id = module.params.get("id", None)
    network_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    networks = []
    if network_id is not None:
        network_box = client.trusted_networks.get_network(network_id=network_id)
        if network_box is None:
            module.fail_json(
                msg="Failed to retrieve Trusted Network ID: '%s'" % (network_id)
            )
        networks = [network_box.to_dict()]
    else:
        networks = client.trusted_networks.list_networks().to_list()
        if network_name is not None:
            network_found = False
            for network in networks:
                if remove_cloud_suffix(network.get("name")) == remove_cloud_suffix(
                    network_name
                ):
                    network_found = True
                    networks = [network]
            if not network_found:
                module.fail_json(
                    msg="Failed to retrieve Trusted Network Name: '%s'" % (network_name)
                )
    module.exit_json(changed=False, data=networks)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
