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
module: zpa_cloud_browser_isolation_banner
short_description: Create a Cloud Browser Isolation Banner
description:
    - This module will create/update/delete a Cloud Browser Isolation Banner
author:
  - William Guilherme (@willguibr)
version_added: "2.0.0"
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
    description: "The unique identifier of the CBI Banner"
    type: str
    required: false
  name:
    description: "Name of the CBI Banner"
    type: str
    required: true
  primary_color:
    description: "Banner Primary Color"
    type: str
    required: false
  text_color:
    description: "Banner Text Color"
    type: str
    required: false
  notification_title:
    description: "Banner Notification Title"
    type: str
    required: false
  notification_text:
    description: "Banner Notification Text"
    type: str
    required: false
  logo:
    description: "Banner Notification Text"
    type: str
    required: false
  banner:
    description: "Show Welcome Notification"
    type: bool
    required: false
    default: true
"""

EXAMPLES = """
- name: Create/Update/Delete a CBI Banner
  zscaler.zpacloud.zpa_cloud_browser_isolation_banner:
    provider: "{{ zpa_cloud }}"
    name: Example CBI Banner
    logo: data:image/png;base64,iVBORw0KGgoAAAANS
    primary_color: "#0076BE"
    text_color: "#FFFFFF"
    banner: true
    notification_title: Heads up, you've been redirected to Browser Isolation!
    notification_text: The website you were trying to access
"""

RETURN = """
# The newly created CBI Banner resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import deleteNone
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def normalize_banner(cbi_banner):
    """
    Remove computed attributes from a cbi banner dict to make comparison easier.
    """
    normalized = cbi_banner.copy() if cbi_banner else {}
    computed_values = ["id"]
    for attr in computed_values:
        normalized.pop(attr, None)
    return normalized


def core(module):
    state = module.params.get("state")
    client = ZPAClientHelper(module)

    # Collect parameters
    params = [
        "id",
        "name",
        "primary_color",
        "text_color",
        "notification_title",
        "notification_text",
        "logo",
        "banner",
    ]
    banner = {param: module.params.get(param) for param in params}
    banner_id = banner.get("id")
    banner_name = banner.get("name")

    # Step 1: Fetch existing banner if possible
    existing_banner = None
    if banner_id:
        result, _unused, error = client.cbi_banner.get_cbi_banner(banner_id)
        if error:
            module.fail_json(
                msg=f"Error retrieving banner by ID {banner_id}: {to_native(error)}"
            )
        if result:
            existing_banner = result.as_dict()

    elif banner_name:
        banner_list, _unused, error = client.cbi_banner.list_cbi_banners()
        if error:
            module.fail_json(msg=f"Error listing CBI banners: {to_native(error)}")
        for item in banner_list or []:
            item_dict = item.as_dict()
            if item_dict.get("name") == banner_name:
                existing_banner = item_dict
                break

    # Step 2: Normalize and compare
    desired_banner = normalize_banner(banner)
    current_banner = normalize_banner(existing_banner) if existing_banner else {}

    fields_to_ignore = ["id"]
    drift = False

    for k in desired_banner:
        if k in fields_to_ignore:
            continue
        if desired_banner.get(k) != current_banner.get(k):
            # module.warn(f"[DRIFT] Key='{k}' => Desired={desired_banner.get(k)!r}, Actual={current_banner.get(k)!r}")
            drift = True

    drift = any(
        desired_banner.get(k) != current_banner.get(k)
        for k in desired_banner
        if k not in fields_to_ignore
    )

    if module.check_mode:
        module.exit_json(
            changed=(state == "present" and (drift or not existing_banner))
            or (state == "absent" and existing_banner)
        )

    # Step 3: Create or Update
    if state == "present":
        if existing_banner:
            if drift:
                update_banner = deleteNone(
                    {
                        "banner_id": existing_banner.get("id"),
                        "name": desired_banner.get("name"),
                        "logo": desired_banner.get("logo"),
                        "primary_color": desired_banner.get("primary_color"),
                        "text_color": desired_banner.get("text_color"),
                        "banner": desired_banner.get("banner"),
                        "notification_title": desired_banner.get("notification_title"),
                        "notification_text": desired_banner.get("notification_text"),
                    }
                )
                updated, _unused, error = client.cbi_banner.update_cbi_banner(
                    banner_id=update_banner.pop("banner_id"), **update_banner
                )
                if error:
                    module.fail_json(
                        msg=f"Error updating CBI Banner: {to_native(error)}"
                    )
                module.exit_json(changed=True, data=updated.as_dict())
            else:
                module.exit_json(changed=False, data=existing_banner)
        else:
            create_banner = deleteNone(
                {
                    "name": desired_banner.get("name"),
                    "logo": desired_banner.get("logo"),
                    "primary_color": desired_banner.get("primary_color"),
                    "text_color": desired_banner.get("text_color"),
                    "banner": desired_banner.get("banner"),
                    "notification_title": desired_banner.get("notification_title"),
                    "notification_text": desired_banner.get("notification_text"),
                }
            )
            created, _unused, error = client.cbi_banner.add_cbi_banner(**create_banner)
            if error:
                module.fail_json(msg=f"Error creating CBI Banner: {to_native(error)}")
            module.exit_json(changed=True, data=created.as_dict())

    # Step 4: Delete
    elif state == "absent" and existing_banner and existing_banner.get("id"):
        _unused, _unused, error = client.cbi_banner.delete_cbi_banner(
            banner_id=existing_banner.get("id"),
        )
        if error:
            module.fail_json(msg=f"Error deleting CBI Banner: {to_native(error)}")
        module.exit_json(changed=True, data=existing_banner)

    module.exit_json(changed=False, data={})


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str", required=False),
        name=dict(type="str", required=True),
        primary_color=dict(type="str", required=False),
        text_color=dict(type="str", required=False),
        notification_title=dict(type="str", required=False),
        notification_text=dict(type="str", required=False),
        logo=dict(type="str", required=False),
        banner=dict(type="bool", default=True, required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
