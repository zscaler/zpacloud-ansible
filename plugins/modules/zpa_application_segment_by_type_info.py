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
module: zpa_application_segment_by_type_info
short_description: Retrieves Application Segments Application Segments by Access Type.
description:
  - This module will retrieve Application Segments by Access Type
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
      - Name of the Application Segment type.
    required: false
    type: str
  application_type:
    description:
      - The type of application segment.
    required: true
    type: str
    choices:
        - BROWSER_ACCESS
        - INSPECT
        - SECURE_REMOTE_ACCESS
"""

EXAMPLES = """
- name: Get details of a specific BROWSER_ACCESS application segment
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: BROWSER_ACCESS

- name: Get details of a specific BROWSER_ACCESS application segment by name
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: BROWSER_ACCESS
    name: ba_app_segment01

- name: Get details of a specific INSPECT application segment
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: INSPECT

- name: Get details of a specific INSPECT application segment by name
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: INSPECT
    name: inspect_app_segment01

- name: Get details of a specific SECURE_REMOTE_ACCESS application segment
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: SECURE_REMOTE_ACCESS

- name: Get details of a specific SECURE_REMOTE_ACCESS application segment by name
  zscaler.zpacloud.zpa_application_segment_by_type_info:
    provider: "{{ zpa_cloud }}"
    application_type: SECURE_REMOTE_ACCESS
    name: pra_app_segment01
"""

RETURN = """
apps:
  description: Details of the application segments retrieved by the specified access type.
  returned: always
  type: list
  elements: dict
  contains:
    app_id:
      description: The unique identifier of the application segment.
      type: str
      sample: "216199618143442006"
    application_port:
      description: The port number used by the application.
      type: str
      sample: "3389"
    application_protocol:
      description: The protocol used by the application.
      type: str
      sample: "RDP"
    connection_security:
      description: The type of connection security used by the application.
      type: str
      sample: "ANY"
    domain:
      description: The domain name associated with the application.
      type: str
      sample: "app01.acme.com"
    enabled:
      description: Indicates if the application segment is enabled.
      type: bool
      sample: true
    hidden:
      description: Indicates if the application segment is hidden.
      type: bool
      sample: false
    id:
      description: The unique identifier of the specific application instance.
      type: str
      sample: "216199618143442008"
    microtenant_name:
      description: The name of the microtenant associated with the application segment.
      type: str
      sample: "Default"
    name:
      description: The name of the application segment.
      type: str
      sample: "app01.acme.com"

changed:
  description: Indicates if any changes were made.
  returned: always
  type: bool
  sample: false

failed:
  description: Indicates if the operation failed.
  returned: always
  type: bool
  sample: false
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    application_type = module.params.get("application_type", None)
    application_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    apps = []

    if application_type is not None:
        apps = client.app_segments.get_segments_by_type(
            application_type=application_type
        ).to_list()
        if application_name is not None:
            app_found = False
            for app in apps:
                if app.get("name") == application_name:
                    app_found = True
                    apps = [app]
            if not app_found:
                module.fail_json(
                    msg="Failed to retrieve Application Segment by Name: '%s'"
                    % (application_name)
                )
    else:
        module.fail_json(msg="Application type must be specified.")

    module.exit_json(changed=False, apps=apps)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        application_type=dict(
            type="str",
            required=True,
            choices=[
                "BROWSER_ACCESS",
                "INSPECT",
                "SECURE_REMOTE_ACCESS",
            ],
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
