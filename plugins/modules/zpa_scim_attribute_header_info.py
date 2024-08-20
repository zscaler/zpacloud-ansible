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
module: zpa_scim_attribute_header_info
short_description: Retrieves scim attribute header from a given IDP
description:
  - This module will allow the retrieval of information about scim attribute header from a given IDP
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
      - Name of the scim attribute.
    required: false
    type: str
  idp_name:
    description:
      - Name of the IDP, required when ID is not sepcified.
    required: true
    type: str
  id:
    description:
      - ID of the scim attribute.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All SCIM Attribute of an IDP
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    idp_name: IdP_Name

- name: Get Information About the SCIM Attribute by Name
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    name: costCenter
    idp_name: IdP_Name

- name: Get Information About the SCIM Attribute by ID
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    id: 216196257331285842
    idp_name: IdP_Name
"""

RETURN = r"""
attributes:
  description: >-
    Details of the SCIM attributes retrieved from the specified Identity Provider (IdP).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the SCIM attribute.
      type: str
      returned: always
      sample: "123456789"
    name:
      description: The name of the SCIM attribute.
      type: str
      returned: always
      sample: "costCenter"
    data_type:
      description: The data type of the SCIM attribute.
      type: str
      returned: always
      sample: "String"
    case_sensitive:
      description: Indicates whether the SCIM attribute is case-sensitive.
      type: bool
      returned: always
      sample: false
    multivalued:
      description: Indicates whether the SCIM attribute is multivalued.
      type: bool
      returned: always
      sample: false
    mutability:
      description: The mutability of the SCIM attribute (e.g., readWrite, immutable).
      type: str
      returned: always
      sample: "readWrite"
    required:
      description: Indicates whether the SCIM attribute is required.
      type: bool
      returned: always
      sample: false
    returned:
      description: Indicates when the SCIM attribute is returned in a response (e.g., always, default).
      type: str
      returned: always
      sample: "default"
    schema_u_r_i:
      description: The schema URI associated with the SCIM attribute.
      type: str
      returned: always
      sample: "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    uniqueness:
      description: Indicates whether the SCIM attribute is unique.
      type: bool
      returned: always
      sample: false
    idp_id:
      description: The unique identifier of the associated Identity Provider (IdP).
      type: str
      returned: always
      sample: "123456789"
    delta:
      description: The delta identifier for the SCIM attribute, used for tracking changes.
      type: str
      returned: always
      sample: "1776f53db627260cddebc5ca748a0982"
    creation_time:
      description: The time when the SCIM attribute was created, in epoch format.
      type: str
      returned: always
      sample: "1651557392"
    modified_by:
      description: The ID of the user who last modified the SCIM attribute.
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
    scim_attr_name = module.params.get("name", None)
    idp_name = module.params.get("idp_name", None)
    scim_attr_id = module.params.get("id", None)
    client = ZPAClientHelper(module)
    idp_id = ""
    idps = client.idp.list_idps()
    for idp in idps:
        if idp.get("name") == idp_name:
            idp_id = idp.get("id")
    if idp_id == "":
        module.fail_json(msg="Failed to retrieve IDP with name : '%s'" % (idp_name))
    attributes = []
    if scim_attr_id is not None:
        attribute_box = client.scim_attributes.get_attribute(
            idp_id=idp_id, attribute_id=scim_attr_id
        )
        if attribute_box is None:
            module.fail_json(
                msg="Failed to retrieve scim attribute header ID: '%s'" % (id)
            )
        attributes = [attribute_box.to_dict()]
    elif scim_attr_name is not None:
        scim_attribute_found = False
        attributes_list = client.scim_attributes.list_attributes_by_idp(
            idp_id=idp_id
        ).to_list()
        for attribute in attributes_list:
            if attribute.get("name") == scim_attr_name:
                scim_attribute_found = True
                attributes = [attribute]
                break
        if not scim_attribute_found:
            module.fail_json(
                msg="Failed to retrieve scim attribute header Name: '%s'"
                % (scim_attr_name)
            )
    else:
        attributes = client.scim_attributes.list_attributes_by_idp(
            idp_id=idp_id
        ).to_list()
    module.exit_json(changed=False, attributes=attributes)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        idp_name=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
