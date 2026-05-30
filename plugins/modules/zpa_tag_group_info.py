#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_tag_group_info
short_description: Retrieve information about ZPA tag groups.
description:
  - Retrieve information for one or more ZPA tag groups.
author:
  - Zscaler Inc. (@zscaler)
version_added: "2.2.0"
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
      - The unique identifier of the tag group.
    required: false
    type: str
  name:
    description:
      - Name of the tag group.
    required: false
    type: str
  microtenant_id:
    description:
      - The unique identifier of the microtenant for the ZPA tenant.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get all tag groups
  zscaler.zpacloud.zpa_tag_group_info:
    provider: "{{ zpa_cloud }}"
"""

RETURN = """
tag_groups:
  description: List of tag groups.
  returned: always
  type: list
  elements: dict
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)
    tag_group_id = module.params.get("id")
    tag_group_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    if tag_group_id:
        result, _unused, error = client.tag_group.get_tag_group(
            tag_group_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve tag group ID '{tag_group_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, tag_groups=[result.as_dict()])

    tag_group_list, error = collect_all_items(
        client.tag_group.list_tag_groups, query_params
    )
    if error:
        module.fail_json(msg=f"Error retrieving tag groups: {to_native(error)}")

    result_list = [item.as_dict() for item in tag_group_list]
    if tag_group_name:
        matched = next(
            (item for item in result_list if item.get("name") == tag_group_name), None
        )
        if not matched:
            module.fail_json(msg=f"Tag group '{tag_group_name}' not found.")
        result_list = [matched]

    module.exit_json(changed=False, tag_groups=result_list)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["id", "name"]],
    )
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
