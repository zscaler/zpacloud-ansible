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
module: zpa_saml_attribute_info
short_description: Retrieves saml attributes from a given IDP
description:
  - This module will allow the retrieval of information about a saml attributes from a given IDP
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

RETURN = r"""
saml_attributes:
  description: >-
    Details of the SAML attributes retrieved from the specified Identity Provider (IdP).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the SAML attribute.
      type: str
      returned: always
      sample: "123456789"
    name:
      description: The name of the SAML attribute.
      type: str
      returned: always
      sample: "DepartmentName_Okta_Users"
    saml_name:
      description: The SAML attribute name.
      type: str
      returned: always
      sample: "DepartmentName"
    idp_id:
      description: The unique identifier of the associated Identity Provider (IdP).
      type: str
      returned: always
      sample: "123456789"
    idp_name:
      description: The name of the associated Identity Provider (IdP).
      type: str
      returned: always
      sample: "Okta_Users"
    user_attribute:
      description: Indicates whether the attribute is a user attribute.
      type: bool
      returned: always
      sample: false
    delta:
      description: The delta identifier for the SAML attribute, used for tracking changes.
      type: str
      returned: always
      sample: "4784a035d62f5353d8115450f20fbc54"
    creation_time:
      description: The time when the SAML attribute was created, in epoch format.
      type: str
      returned: always
      sample: "1651557323"
    modified_by:
      description: The ID of the user who last modified the SAML attribute.
      type: str
      returned: always
      sample: "123456789"
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
        attributes = client.saml_attributes.list_attributes(pagesize=500).to_list()
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
    module.exit_json(changed=False, saml_attributes=saml_attributes)


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
