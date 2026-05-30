#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_tag_namespace_info
short_description: Retrieve information about ZPA tag namespaces.
description:
  - Retrieve information for one or more ZPA tag namespaces.
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
      - The unique identifier of the tag namespace.
    required: false
    type: str
  name:
    description:
      - Name of the tag namespace.
    required: false
    type: str
  microtenant_id:
    description:
      - The unique identifier of the microtenant for the ZPA tenant.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get all tag namespaces
  zscaler.zpacloud.zpa_tag_namespace_info:
    provider: "{{ zpa_cloud }}"

- name: Get a namespace by name
  zscaler.zpacloud.zpa_tag_namespace_info:
    provider: "{{ zpa_cloud }}"
    name: "Environment"
"""

RETURN = """
namespaces:
  description: List of tag namespaces.
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
    namespace_id = module.params.get("id")
    namespace_name = module.params.get("name")
    microtenant_id = module.params.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    if namespace_id:
        result, _unused, error = client.tag_namespace.get_namespace(
            namespace_id, query_params
        )
        if error or result is None:
            module.fail_json(
                msg=f"Failed to retrieve tag namespace ID '{namespace_id}': {to_native(error)}"
            )
        module.exit_json(changed=False, namespaces=[result.as_dict()])

    namespace_list, error = collect_all_items(
        client.tag_namespace.list_namespaces, query_params
    )
    if error:
        module.fail_json(msg=f"Error retrieving tag namespaces: {to_native(error)}")

    result_list = [item.as_dict() for item in namespace_list]
    if namespace_name:
        matched = next(
            (item for item in result_list if item.get("name") == namespace_name), None
        )
        if not matched:
            module.fail_json(msg=f"Tag namespace '{namespace_name}' not found.")
        result_list = [matched]

    module.exit_json(changed=False, namespaces=result_list)


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
