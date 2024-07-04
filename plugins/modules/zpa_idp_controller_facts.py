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
module: zpa_idp_controller_facts
short_description: Retrieves Identity Provider information.
description:
  - This module will allow the retrieval of information about an Identity Provider (IdP) detail from the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)

extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation

options:
  name:
    description:
      - Name of the Identity Provider.
    required: false
    type: str
  id:
    description:
      - ID of the Identity Provider.
    required: false
    type: str
  state:
      description:
          - The state of the module, which determines if the settings are to be applied.
      type: str
      choices: ['gathered']
      default: 'gathered'
"""

EXAMPLES = """
- name: Get Details of All IdP Controllers
  zscaler.zpacloud.zpa_idp_controller_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Details of a Specific IdP Controller by Name
  zscaler.zpacloud.zpa_idp_controller_facts:
    provider: "{{ zpa_cloud }}"
    name: User_IdP_Name

- name: Get Details of a Specific IdP Controller by ID
  zscaler.zpacloud.zpa_idp_controller_facts:
    provider: "{{ zpa_cloud }}"
    id: "216196257331282583"
"""

RETURN = """
# Returns information on a specified Identity Provider.
"""

from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    idp_id = module.params.get("id", None)
    idp_name = module.params.get("name", None)
    state = module.params.get("state", None)  # Get the state parameter
    client = ZPAClientHelper(module)

    if state == "gathered":
        # Logic for the gathered state
        idps = []
        if idp_id is not None:
            idp_box = client.idp.get_idp(idp_id=idp_id)
            if idp_box is None:
                module.fail_json(
                    msg="Failed to retrieve Identity Provider ID: '%s'" % (idp_id)
                )
            idps = [idp_box.to_dict()]
        else:
            idps = client.idp.list_idps(pagesize=500).to_list()
            if idp_name is not None:
                idp_found = False
                for idp in idps:
                    if idp.get("name") == idp_name:
                        idp_found = True
                        idps = [idp]
                if not idp_found:
                    module.fail_json(
                        msg="Failed to retrieve Identity Provider Name: '%s'"
                        % (idp_name)
                    )
        module.exit_json(changed=False, data=idps)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        state=dict(
            type="str", choices=["gathered"], default="gathered"
        ),  # Add state parameter
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
