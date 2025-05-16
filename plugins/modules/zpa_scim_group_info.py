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
module: zpa_scim_group_info
short_description: Retrieves scim group information from a given IDP
description:
  - This module will allow the retrieval of information about scim group(s) from a given IDP
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
      - Name of the scim group.
    required: false
    type: str
  idp_name:
    description:
      - Name of the IDP.
    required: true
    type: str
  id:
    description:
      - ID of the scim group.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Information About All SCIM Groups from an IdP
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    idp_name: "IdP_Name"

- name: Get Information About a SCIM Group by ID
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    id: 216196257331285827
    idp_name: "IdP_Name"

- name: Get Information About a SCIM Group by Name
  zscaler.zpacloud.zpa_scim_attribute_header_facts:
    provider: "{{ zpa_cloud }}"
    name: "Finance"
    idp_name: "IdP_Name"
"""

RETURN = r"""
data:
  description: >-
    Details of the SCIM groups retrieved from the specified Identity Provider (IdP).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the SCIM group.
      type: int
      returned: always
      sample: 645699
    name:
      description: The name of the SCIM group.
      type: str
      returned: always
      sample: "Engineering"
    creation_time:
      description: The time when the SCIM group was created, in epoch format.
      type: int
      returned: always
      sample: 1651557507
    modified_time:
      description: The time when the SCIM group was last modified, in epoch format.
      type: int
      returned: always
      sample: 1651557507
    idp_id:
      description: The unique identifier of the associated Identity Provider (IdP).
      type: int
      returned: always
      sample: 123456789
    internal_id:
      description: The internal identifier of the SCIM group.
      type: str
      returned: always
      sample: "645699"
    idp_group_id:
      description: The group ID in the IdP system, if available.
      type: str
      returned: when available
      sample: null
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def core(module):
    scim_group_name = module.params.get("name")
    scim_group_id = module.params.get("id")
    idp_name = module.params.get("idp_name")
    client = ZPAClientHelper(module)

    # Build query parameters from supported fields
    supported_params = [
        "start_time",
        "end_time",
        "idp_group_id",
        "scim_user_id",
        "scim_user_name",
        "search",
        "sort_order",
        "sort_by",
        "all_entries",
    ]
    query_params = {}
    for param in supported_params:
        val = module.params.get(param)
        if val is not None:
            query_params[param] = val

    # Lookup IdP ID from provided idp_name
    idps, _, err = client.idp.list_idps(query_params={"search": idp_name})
    if err:
        module.fail_json(msg=f"Error searching for IdP '{idp_name}': {to_native(err)}")
    idp_id = next((idp.id for idp in idps if idp.name == idp_name), None)
    if not idp_id:
        module.fail_json(msg=f"IdP with name '{idp_name}' not found")

    # Get SCIM group by ID
    if scim_group_id:
        result, _, err = client.scim_groups.get_scim_group(scim_group_id)
        if err or not result:
            module.fail_json(
                msg=f"SCIM group with ID '{scim_group_id}' not found: {to_native(err)}"
            )
        module.exit_json(changed=False, data=[result.as_dict()])

    # Warn log before pagination call
    # module.warn(f"[SCIM Groups] Fetching all portals with query_params: {query_params}")

    # Get SCIM group by name
    if scim_group_name:
        query_params["search"] = scim_group_name
        groups, err = collect_all_items(
            lambda qp: client.scim_groups.list_scim_groups(
                idp_id=idp_id, query_params=qp
            ),
            query_params,
        )
        if err:
            module.fail_json(msg=f"Error searching SCIM groups: {to_native(err)}")
        matched = next(
            (
                g
                for g in groups
                if g.name == scim_group_name or g.get("name") == scim_group_name
            ),
            None,
        )
        if not matched:
            module.fail_json(msg=f"SCIM group with name '{scim_group_name}' not found")
        module.exit_json(
            changed=False,
            data=[matched.as_dict() if hasattr(matched, "as_dict") else matched],
        )

    # List all SCIM groups for the given IdP
    groups, err = collect_all_items(
        lambda qp: client.scim_groups.list_scim_groups(idp_id=idp_id, query_params=qp),
        query_params,
    )
    if err:
        module.fail_json(msg=f"Error listing SCIM groups: {to_native(err)}")

    # module.warn(f"[SCIM Groups] Total groups retrieved: {len(groups)}")

    # ✅ Safely serialize model instances or dicts
    module.exit_json(
        changed=False,
        data=[g.as_dict() if hasattr(g, "as_dict") else g for g in groups],
    )


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        idp_name=dict(type="str", required=True),
        start_time=dict(type="str", required=False),
        end_time=dict(type="str", required=False),
        idp_group_id=dict(type="str", required=False),
        scim_user_id=dict(type="str", required=False),
        scim_user_name=dict(type="str", required=False),
        search=dict(type="str", required=False),
        sort_order=dict(type="str", required=False, choices=["ASC", "DSC"]),
        sort_by=dict(type="str", required=False),
        all_entries=dict(type="bool", required=False, default=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
