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
module: zpa_app_connector_controller_facts
short_description: Retrieves an app connector controller information
description:
  - This module will allow the retrieval of information about an app connector controller.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider

options:
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

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
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
