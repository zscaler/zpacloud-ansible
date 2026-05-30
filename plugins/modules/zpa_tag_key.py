#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_tag_key
short_description: Manage ZPA tag keys.
description:
  - Create, update, or delete ZPA tag keys within a namespace.
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
      - The unique identifier of the tag key.
    type: str
    required: false
  namespace_id:
    description:
      - The unique identifier of the parent tag namespace.
    type: str
    required: true
  name:
    description:
      - Name of the tag key.
    type: str
    required: true
  description:
    description:
      - Description of the tag key.
    type: str
    required: false
  enabled:
    description:
      - Whether the tag key is enabled.
    type: bool
    required: false
    default: true
  tag_values:
    description:
      - List of tag values attached to this tag key.
    type: list
    elements: dict
    required: false
  microtenant_id:
    description:
      - The unique identifier of the microtenant for the ZPA tenant.
    type: str
    required: false
"""

EXAMPLES = """
- name: Create or update a tag key
  zscaler.zpacloud.zpa_tag_key:
    provider: "{{ zpa_cloud }}"
    namespace_id: "216199618143442000"
    name: "Environment"
    description: "Deployment environment"
    enabled: true
    tag_values:
      - name: "dev"
      - name: "prod"
"""

RETURN = """
data:
  description: Tag key details.
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
    user_provided_tag_values = module.params.get("tag_values") is not None

    desired = {
        "id": module.params.get("id"),
        "namespace_id": module.params.get("namespace_id"),
        "name": module.params.get("name"),
        "description": module.params.get("description"),
        "enabled": module.params.get("enabled"),
        "tag_values": module.params.get("tag_values"),
        "microtenant_id": module.params.get("microtenant_id"),
    }
    tag_key_id = desired.get("id")
    tag_key_name = desired.get("name")
    namespace_id = desired.get("namespace_id")
    microtenant_id = desired.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    existing_tag_key = None
    if tag_key_id:
        result, _unused, error = client.tag_key.get_tag_key(
            namespace_id, tag_key_id, query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving tag key by ID {tag_key_id}: {to_native(error)}"
            )
        if result:
            existing_tag_key = result.as_dict()
    elif tag_key_name:
        tag_keys, error = collect_all_items(
            lambda qp: client.tag_key.list_tag_keys(namespace_id, qp), query_params
        )
        if error:
            module.fail_json(msg=f"Error listing tag keys: {to_native(error)}")
        for item in tag_keys or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == tag_key_name:
                # Fetch full object to avoid summary/list response drift.
                details_result = client.tag_key.get_tag_key(
                    namespace_id, item_dict.get("id"), query_params
                )
                if isinstance(details_result, tuple) and len(details_result) == 3:
                    details, _unused, details_error = details_result
                    if details_error:
                        module.fail_json(
                            msg=f"Error retrieving tag key by ID {item_dict.get('id')}: {to_native(details_error)}"
                        )
                    existing_tag_key = details.as_dict() if details else item_dict
                else:
                    existing_tag_key = item_dict
                break

    desired_norm = normalize_app(desired)
    current_norm = normalize_app(existing_tag_key) if existing_tag_key else {}
    fields_to_exclude = ["id"]
    if not user_provided_tag_values:
        fields_to_exclude.append("tag_values")
    elif existing_tag_key and not current_norm.get("tag_values"):
        # Some API responses omit/empty tag_values even when configured.
        fields_to_exclude.append("tag_values")

    drift = any(
        desired_norm.get(k) != current_norm.get(k)
        for k in desired_norm
        if k not in fields_to_exclude and k in current_norm
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_tag_key))
            or (state == "absent" and existing_tag_key)
        )

    if state == "present":
        payload = deleteNone(
            {
                "name": desired_norm.get("name"),
                "description": desired_norm.get("description"),
                "enabled": desired_norm.get("enabled"),
                "namespaceId": desired_norm.get("namespace_id"),
                "tagValues": desired_norm.get("tag_values"),
                "microtenantId": desired_norm.get("microtenant_id"),
            }
        )
        request_obj = RequestBodyObject(payload)
        if existing_tag_key:
            if drift:
                updated, _unused, error = client.tag_key.update_tag_key(
                    namespace_id, existing_tag_key.get("id"), request_obj, query_params
                )
                if error:
                    module.fail_json(msg=f"Error updating tag key: {to_native(error)}")
                module.exit_json(changed=True, data=updated.as_dict())
            module.exit_json(changed=False, data=existing_tag_key)
        created, _unused, error = client.tag_key.create_tag_key(
            namespace_id, request_obj, query_params
        )
        if error:
            module.fail_json(msg=f"Error creating tag key: {to_native(error)}")
        module.exit_json(changed=True, data=created.as_dict())

    if state == "absent" and existing_tag_key and existing_tag_key.get("id"):
        _unused, _unused, error = client.tag_key.delete_tag_key(
            namespace_id, existing_tag_key.get("id"), query_params
        )
        if error:
            module.fail_json(msg=f"Error deleting tag key: {to_native(error)}")
        module.exit_json(changed=True, data=existing_tag_key)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        namespace_id=dict(type="str", required=True),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False, default=True),
        tag_values=dict(type="list", elements="dict", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
