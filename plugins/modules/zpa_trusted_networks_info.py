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

module: zpa_trusted_networks_info
short_description: Retrieves information about a Trusted Network.
description:
    - This module will allow the retrieval of information about Trusted Network resource.
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
  microtenant_id:
      description:
      - The unique identifier of the Microtenant for the ZPA tenant
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

RETURN = r"""
networks:
  description: >-
    Details of the Trusted Networks.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the Trusted Network.
      type: str
      returned: always
      sample: "216199618143266948"
    name:
      description: The name of the Trusted Network.
      type: str
      returned: always
      sample: "BDTrustedNetwork01 (zscalertwo.net)"
    creation_time:
      description: The time when the Trusted Network was created, in epoch format.
      type: str
      returned: always
      sample: "1698786462"
    modified_time:
      description: The time when the Trusted Network was last modified, in epoch format.
      type: str
      returned: always
      sample: "1698786462"
    modified_by:
      description: The ID of the user who last modified the Trusted Network.
      type: str
      returned: always
      sample: "72057594037928115"
    network_id:
      description: The unique network identifier for the Trusted Network.
      type: str
      returned: always
      sample: "aeba3ac7-d860-4fa4-b4b8-8936ed7bc686"
    zscaler_cloud:
      description: The Zscaler cloud where the Trusted Network is configured.
      type: str
      returned: always
      sample: "zscalertwo"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
    remove_cloud_suffix,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    network_id = module.params.get("id")
    network_name = module.params.get("name")
    client = ZPAClientHelper(module)

    # Lookup by ID
    if network_id is not None:
        network_box = client.trusted_networks.get_network(network_id=network_id)
        if network_box is None:
            module.fail_json(
                msg=f"Failed to retrieve Trusted Network ID: '{network_id}'"
            )
        result = [
            network_box.as_dict() if hasattr(network_box, "as_dict") else network_box
        ]
        module.exit_json(changed=False, networks=result)

    # Fetch all with pagination
    module.warn("[Trusted Network] Fetching all networks with pagination")
    networks, err = collect_all_items(client.trusted_networks.list_trusted_networks, {})
    if err:
        module.fail_json(msg=f"Error retrieving Trusted Networks: {to_native(err)}")

    module.warn(f"[Trusted Network] Total networks retrieved: {len(networks)}")

    # Search by name using suffix-stripped comparison
    if network_name:
        normalized_input = remove_cloud_suffix(network_name)
        match = next(
            (
                n
                for n in networks
                if remove_cloud_suffix(getattr(n, "name", "")) == normalized_input
            ),
            None,
        )
        if not match:
            available = [remove_cloud_suffix(getattr(n, "name", "")) for n in networks]
            module.fail_json(
                msg=f"Trusted Network '{network_name}' not found. Available: {available}"
            )
        networks = [match]

    result = [n.as_dict() if hasattr(n, "as_dict") else n for n in networks]
    module.exit_json(changed=False, networks=result)


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
