#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, Zscaler Technology Alliances <zscaler-partner-labs@z-bd.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_app_connector_controller_info
short_description: Retrieves an app connector controller information
description:
  - This module will allow the retrieval of information about an app connector controller.
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
      - Name of the App Connector Group.
    required: false
    type: str
  id:
    description:
      - ID of the App Connector Group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Retrieve Details of all App Connector Groups
  zscaler.zpacloud.zpa_app_connector_controller_info:

- name: Retrieve Details of a Specific App Connector Groups by Name
  zscaler.zpacloud.zpa_app_connector_controller_info:
    name: "Example App Connector Group"

- name: Retrieve Details of a Specific App Connector Groups by ID
  zscaler.zpacloud.zpa_app_connector_controller_info:
    id: "216196257331292046"
"""

RETURN = """
# Returns information on a specified App Connector Group.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module: AnsibleModule):
    connector_id = module.params.get("id", None)
    connector_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    connectors = []
    if connector_id is not None:
        connector_box = client.connectors.get_connector(connector_id=connector_id)
        if connector_box is None:
            module.fail_json(
                msg="Failed to retrieve App Connector ID: '%s'" % (connector_id)
            )
        connectors = [connector_box.to_dict()]
    else:
        connectors = client.connectors.list_connectors().to_list()
        if connector_name is not None:
            connector_found = False
            for connector in connectors:
                if connector.get("name") == connector_name:
                    connector_found = True
                    connectors = [connector]
            if not connector_found:
                module.fail_json(
                    msg="Failed to retrieve App Connector Name: '%s'" % (connector_name)
                )
    module.exit_json(changed=False, data=connectors)


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
