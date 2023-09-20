#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
options:
  client_id:
    description: ""
    required: false
    type: str
  client_secret:
    description: ""
    required: false
    type: str
  customer_id:
    description: ""
    required: false
    type: str
  name:
    description:
      - Name of the trusted network.
    required: false
    type: str
  id:
    description:
      - ID of the trusted network.
    required: false
    type: str

"""

EXAMPLES = """
- name: Get Information About All Trusted Networks
  zscaler.zpacloud.zpa_trusted_network_info:
- name: Get information about Trusted Networks by Name
  zscaler.zpacloud.zpa_trusted_network_info:
    name: Corp-Trusted-Networks
- name: Get information about Trusted Networks by ID
  zscaler.zpacloud.zpa_trusted_network_info:
    id: 216196257331282234
"""

RETURN = """
# Returns information on a specified Trusted Network.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
import re


def remove_cloud_suffix(s: str) -> str:
    reg = re.compile(r"(.*)[\s]+\([a-zA-Z0-9\-_\.]*\)[\s]*$")
    res = reg.sub(r"\1", s)
    return res.strip()


def core(module: AnsibleModule):
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
