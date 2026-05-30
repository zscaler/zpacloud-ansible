#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_tag_namespace
short_description: Manage ZPA tag namespaces.
description:
  - Create, update, or delete ZPA tag namespaces.
author:
  - Zscaler Inc. (@zscaler)
version_added: "2.2.0"
requirements:
  - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
notes:
  - Check mode is supported.
extends_documentation_fragment:
  - zscaler.zpacloud.fragments.provider
  - zscaler.zpacloud.fragments.documentation
  - zscaler.zpacloud.fragments.state
options:
  id:
    description:
      - The unique identifier of the tag namespace.
    type: str
    required: false
  name:
    description:
      - Name of the tag namespace.
    type: str
    required: true
  description:
    description:
      - Description of the tag namespace.
    type: str
    required: false
  enabled:
    description:
      - Whether the namespace is enabled.
    type: bool
    required: false
    default: true
  microtenant_id:
    description:
      - The unique identifier of the microtenant for the ZPA tenant.
    type: str
    required: false
  origin:
    description:
      - The origin of the tag namespace.
    type: str
    required: false
    default: CUSTOM
"""

EXAMPLES = """
- name: Create or update a tag namespace
  zscaler.zpacloud.zpa_tag_namespace:
    provider: "{{ zpa_cloud }}"
    name: "Environment"
    description: "Environment namespace"
    enabled: true
    origin: "CUSTOM"
"""

RETURN = """
data:
  description: Tag namespace details.
  returned: always
  type: dict
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    normalize_app,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


class RequestBodyObject:
    def __init__(self, payload):
        self.payload = payload

    def request_format(self):
        return self.payload


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    desired = {
        "id": module.params.get("id"),
        "name": module.params.get("name"),
        "description": module.params.get("description"),
        "enabled": module.params.get("enabled"),
        "microtenant_id": module.params.get("microtenant_id"),
        "origin": module.params.get("origin"),
    }
    namespace_id = desired.get("id")
    namespace_name = desired.get("name")
    microtenant_id = desired.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    existing_namespace = None
    if namespace_id:
        result, _unused, error = client.tag_namespace.get_namespace(
            namespace_id, query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving tag namespace by ID {namespace_id}: {to_native(error)}"
            )
        if result:
            existing_namespace = result.as_dict()
    elif namespace_name:
        namespaces, error = collect_all_items(
            client.tag_namespace.list_namespaces, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing tag namespaces: {to_native(error)}")
        for item in namespaces or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == namespace_name:
                existing_namespace = item_dict
                break

    desired_norm = normalize_app(desired)
    current_norm = normalize_app(existing_namespace) if existing_namespace else {}
    drift = any(
        desired_norm.get(k) != current_norm.get(k)
        for k in desired_norm
        if k not in ["id"]
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_namespace))
            or (state == "absent" and existing_namespace)
        )

    if state == "present":
        payload = deleteNone(
            {
                "name": desired_norm.get("name"),
                "description": desired_norm.get("description"),
                "enabled": desired_norm.get("enabled"),
                "microtenantId": desired_norm.get("microtenant_id"),
                "origin": desired_norm.get("origin"),
            }
        )
        request_obj = RequestBodyObject(payload)
        if existing_namespace:
            if drift:
                updated, _unused, error = client.tag_namespace.update_namespace(
                    existing_namespace.get("id"), request_obj, query_params
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating tag namespace: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            module.exit_json(changed=False, data=existing_namespace)
        created, _unused, error = client.tag_namespace.create_namespace(
            request_obj, query_params
        )
        if error:
            module.fail_json(msg=f"Error creating tag namespace: {to_native(error)}")
        module.exit_json(changed=True, data=created.as_dict())

    if state == "absent" and existing_namespace and existing_namespace.get("id"):
        _unused, _unused, error = client.tag_namespace.delete_namespace(
            existing_namespace.get("id"), query_params
        )
        if error:
            module.fail_json(msg=f"Error deleting tag namespace: {to_native(error)}")
        module.exit_json(changed=True, data=existing_namespace)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        origin=dict(type="str", required=False, default="CUSTOM"),
        enabled=dict(type="bool", required=False, default=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
