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
module: zpa_saml_attribute_facts
short_description: Retrieves saml attributes from a given IDP
description:
  - This module will allow the retrieval of information about a saml attributes from a given IDP
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
      - Name of the saml attribute.
    required: false
    type: str
  id:
    description:
      - ID of the saml attribute.
    required: false
    type: str
  idp_name:
    description:
      - Name of the IDP.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All SAML Attributes
  zscaler.zpacloud.zpa_saml_attribute_facts:
    provider: "{{ zpa_cloud }}"

- name: Get Information About Saml Attribute by Attribute Name
  zscaler.zpacloud.zpa_saml_attribute_facts:
    provider: "{{ zpa_cloud }}"
    name: DepartmentName_User

- name: Get Information About Saml Attribute by Attribute ID
  zscaler.zpacloud.zpa_saml_attribute_facts:
    provider: "{{ zpa_cloud }}"
    id: 216196257331285827
"""

RETURN = """
# Returns information on a specified SAML attribute.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    saml_attr_name = module.params.get("name", None)
    saml_attr_id = module.params.get("id", None)
    idp_name = module.params.get("idp_name", None)
    client = ZPAClientHelper(module)
    saml_attributes = []
    if saml_attr_id is not None:
        attribute_box = client.saml_attributes.get_attribute(attribute_id=saml_attr_id)
        if attribute_box is None:
            module.fail_json(msg="Failed to retrieve saml attribute ID: '%s'" % (id))
        saml_attributes = [attribute_box.to_dict()]
    elif saml_attr_name is not None:
        attributes = client.saml_attributes.list_attributes().to_list()
        if attributes is None:
            module.fail_json(
                msg="Failed to retrieve saml attribute Name: '%s'" % (saml_attr_name)
            )
        saml_attr_found = False
        for saml_attribute in attributes:
            if saml_attribute.get("name") == saml_attr_name:
                saml_attr_found = True
                saml_attributes = [saml_attribute]
        if not saml_attr_found:
            module.fail_json(
                msg="Failed to retrieve SAML attribute Name: '%s'" % (saml_attr_name)
            )
    elif idp_name is not None:
        idp_id = ""
        idps = client.idp.list_idps()
        for idp in idps:
            if idp.get("name") == idp_name:
                idp_id = idp.get("id")
        saml_attributes = client.saml_attributes.list_attributes_by_idp(
            idp_id=idp_id
        ).to_list()
    else:
        saml_attributes = client.saml_attributes.list_attributes().to_list()
    module.exit_json(changed=False, data=saml_attributes)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        idp_name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
