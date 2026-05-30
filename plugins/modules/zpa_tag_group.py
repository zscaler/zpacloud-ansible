#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_tag_group
short_description: Manage ZPA tag groups.
description:
  - Create, update, or delete ZPA tag groups.
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
      - The unique identifier of the tag group.
    type: str
    required: false
  name:
    description:
      - Name of the tag group.
    type: str
    required: true
  description:
    description:
      - Description of the tag group.
    type: str
    required: false
  tags:
    description:
      - Tags associated with this tag group.
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
- name: Create or update a tag group
  zscaler.zpacloud.zpa_tag_group:
    provider: "{{ zpa_cloud }}"
    name: "Prod-Workloads"
    description: "Production workload tags"
    tags:
      - namespace:
          id: "216199618143442000"
        tagKey:
          id: "216199618143442001"
        tagValue:
          name: "prod"
"""

RETURN = """
data:
  description: Tag group details.
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
    user_provided_tags = module.params.get("tags") is not None

    desired = {
        "id": module.params.get("id"),
        "name": module.params.get("name"),
        "description": module.params.get("description"),
        "tags": module.params.get("tags"),
        "microtenant_id": module.params.get("microtenant_id"),
    }
    tag_group_id = desired.get("id")
    tag_group_name = desired.get("name")
    microtenant_id = desired.get("microtenant_id")
    query_params = {"microtenant_id": microtenant_id} if microtenant_id else {}

    existing_tag_group = None
    if tag_group_id:
        result, _unused, error = client.tag_group.get_tag_group(
            tag_group_id, query_params
        )
        if error:
            module.fail_json(
                msg=f"Error retrieving tag group by ID {tag_group_id}: {to_native(error)}"
            )
        if result:
            existing_tag_group = result.as_dict()
    elif tag_group_name:
        tag_groups, error = collect_all_items(
            client.tag_group.list_tag_groups, query_params
        )
        if error:
            module.fail_json(msg=f"Error listing tag groups: {to_native(error)}")
        for item in tag_groups or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == tag_group_name:
                existing_tag_group = item_dict
                break

    desired_norm = normalize_app(desired)
    current_norm = normalize_app(existing_tag_group) if existing_tag_group else {}
    fields_to_exclude = ["id"]
    if not user_provided_tags:
        # API may omit tags in GET responses, and users may not want to manage
        # tags for this resource invocation when they are not explicitly set.
        fields_to_exclude.append("tags")

    drift = any(
        desired_norm.get(k) != current_norm.get(k)
        for k in desired_norm
        if k not in fields_to_exclude
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_tag_group))
            or (state == "absent" and existing_tag_group)
        )

    if state == "present":
        payload = deleteNone(
            {
                "name": desired_norm.get("name"),
                "description": desired_norm.get("description"),
                "tags": desired_norm.get("tags"),
                "microtenantId": desired_norm.get("microtenant_id"),
            }
        )
        request_obj = RequestBodyObject(payload)
        if existing_tag_group:
            if drift:
                updated, _unused, error = client.tag_group.update_tag_group(
                    existing_tag_group.get("id"), request_obj, query_params
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating tag group: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            module.exit_json(changed=False, data=existing_tag_group)
        created, _unused, error = client.tag_group.create_tag_group(
            request_obj, query_params
        )
        if error:
            module.fail_json(msg=f"Error creating tag group: {to_native(error)}")
        module.exit_json(changed=True, data=created.as_dict())

    if state == "absent" and existing_tag_group and existing_tag_group.get("id"):
        _unused, _unused, error = client.tag_group.delete_tag_group(
            existing_tag_group.get("id"), query_params
        )
        if error:
            module.fail_json(msg=f"Error deleting tag group: {to_native(error)}")
        module.exit_json(changed=True, data=existing_tag_group)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        tags=dict(type="list", elements="dict", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
