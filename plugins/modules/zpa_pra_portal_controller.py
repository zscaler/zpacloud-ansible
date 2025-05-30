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
module: zpa_pra_portal_controller
short_description: Create a PRA Portal Controller.
description:
  - This module will create/update/delete Privileged Remote Access Portal.
author:
  - William Guilherme (@willguibr)
version_added: "1.1.0"
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
    type: str
    description: "The unique identifier of the privileged portal"
    required: false
  name:
    type: str
    description: "The name of the privileged portal"
    required: true
  description:
    type: str
    description: "The description of the privileged portal"
    required: false
  enabled:
    type: bool
    description:
        - Whether or not the privileged portal is enabled
    required: false
    default: true
  domain:
    type: str
    description:
        - The domain of the privileged portal
    required: false
  certificate_id:
    type: str
    description:
        - The unique identifier of the certificate
    required: false
  user_notification:
    type: str
    description:
        - The notification message displayed in the banner of the privileged portallink, if enabled
    required: false
  user_notification_enabled:
    type: bool
    description:
        - Indicates if the Notification Banner is enabled (true) or disabled (false)
    required: false
    default: true
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant
    required: false
    type: str
"""

EXAMPLES = """
- name: Gather Details of a Specific Browser Certificates by Name
  zscaler.zpacloud.zpa_ba_certificate_info:
    provider: '{{ zpa_cloud }}'
    name: 'portal.acme.com'
  register: cert_name

- name: Create/Update/Delete PRA Portal
  zscaler.zpacloud.zpa_pra_portal_controller:
    provider: '{{ zpa_cloud }}'
    name: 'portal.acme.com'
    description: 'Created with Ansible'
    enabled: true
    domain: 'portal.acme.com'
    certificate_id: "{{ cert_name.data[0].id }}"
    user_notification: 'Created with Ansible'
    user_notification_enabled: true
  register: result
"""

RETURN = """
# The newly created privileged portal resource record.
"""


from traceback import format_exc
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
    collect_all_items,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_creds(portal):
    """
    Normalize pra portal data by setting computed values.
    """
    normalized = portal.copy()

    computed_values = []
    for attr in computed_values:
        normalized.pop(attr, None)

    return normalized


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    portal = dict()
    params = [
        "id",
        "microtenant_id",
        "name",
        "description",
        "enabled",
        "domain",
        "certificate_id",
        "user_notification",
        "user_notification_enabled",
    ]
    for param_name in params:
        portal[param_name] = module.params.get(param_name, None)

    portal_id = portal.get("id", None)
    portal_name = portal.get("name", None)
    microtenant_id = module.params.get("microtenant_id")

    query_params = {}
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    existing_portal = None
    if portal_id is not None:
        result, _unused, error = client.pra_portal.get_portal(
            portal_id, query_params={"microtenant_id": microtenant_id}
        )
        if error:
            module.fail_json(
                msg=f"Error fetching pra portal with id {portal_id}: {to_native(error)}"
            )
        existing_portal = result.as_dict()
    else:
        result, error = collect_all_items(client.pra_portal.list_portals, query_params)
        if error:
            module.fail_json(msg=f"Error pra portals: {to_native(error)}")
        if result:
            for portal_ in result:
                if portal_.name == portal_name:
                    existing_portal = portal_.as_dict()
                    break

    desired_portal = normalize_creds(portal)
    current_portal = normalize_creds(existing_portal) if existing_portal else {}

    fields_to_exclude = ["id"]
    differences_detected = False
    for key, value in desired_portal.items():
        if key not in fields_to_exclude and current_portal.get(key) != value:
            differences_detected = True
            module.warn(
                f"Difference detected in {key}. Current: {current_portal.get(key)}, Desired: {value}"
            )

    if module.check_mode:
        # If in check mode, report changes and exit
        if state == "present" and (existing_portal is None or differences_detected):
            module.exit_json(changed=True)
        elif state == "absent" and existing_portal is not None:
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)

    if existing_portal is not None:
        id = existing_portal.get("id")
        existing_portal.update(portal)
        existing_portal["id"] = id

    module.warn(f"Final payload being sent to SDK: {portal}")
    if state == "present":
        if existing_portal is not None:
            if differences_detected:
                """Update"""
                update_portal = deleteNone(
                    {
                        "portal_id": existing_portal.get("id"),
                        "microtenant_id": desired_portal.get("microtenant_id", None),
                        "name": desired_portal.get("name"),
                        "description": desired_portal.get("description"),
                        "enabled": desired_portal.get("enabled"),
                        "domain": desired_portal.get("domain"),
                        "certificate_id": desired_portal.get("certificate_id"),
                        "user_notification": desired_portal.get("user_notification"),
                        "user_notification_enabled": desired_portal.get(
                            "user_notification_enabled"
                        ),
                    }
                )
                module.warn("Payload Update for SDK: {}".format(update_portal))
                updated_portal, _unused, error = client.pra_portal.update_portal(
                    portal_id=update_portal.pop("portal_id"), **existing_portal
                )
                if error:
                    module.fail_json(msg=f"Error updating portal: {to_native(error)}")
                module.exit_json(changed=True, data=updated_portal.as_dict())
            else:
                module.exit_json(changed=False, data=existing_portal)
        else:
            module.warn("Creating pra portal as no existing portal was found")
            """Create"""
            create_portal = deleteNone(
                {
                    "microtenant_id": desired_portal.get("microtenant_id", None),
                    "name": desired_portal.get("name"),
                    "description": desired_portal.get("description"),
                    "enabled": desired_portal.get("enabled"),
                    "domain": desired_portal.get("domain"),
                    "certificate_id": desired_portal.get("certificate_id"),
                    "user_notification": desired_portal.get("user_notification"),
                    "user_notification_enabled": desired_portal.get(
                        "user_notification_enabled"
                    ),
                }
            )
            module.warn(f"Payload for SDK: {create_portal}")
            new_portal, _unused, error = client.pra_portal.add_portal(**create_portal)
            if error:
                module.fail_json(msg=f"Error creating portal: {to_native(error)}")
            module.exit_json(changed=True, data=new_portal.as_dict())

    elif state == "absent":
        if existing_portal:
            _unused, _unused, error = client.pra_portal.delete_portal(
                portal_id=existing_portal.get("id"),
                microtenant_id=microtenant_id,
            )
            if error:
                module.fail_json(msg=f"Error deleting portal: {to_native(error)}")
            module.exit_json(changed=True, data=existing_portal)
        module.exit_json(changed=False, data=None)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        microtenant_id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False, default=True),
        domain=dict(type="str", required=False),
        certificate_id=dict(type="str", required=False),
        user_notification=dict(type="str", required=False),
        user_notification_enabled=dict(type="bool", required=False, default=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
