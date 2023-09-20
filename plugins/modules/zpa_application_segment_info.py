#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2022, William Guilherme <wguilherme@securitygeek.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: zpa_application_segment_info
short_description: Retrieve an application segment information.
description:
    - This module will allow the retrieval of information about an application segment.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
options:
  client_id:
    description: ""
    required: false
    type: str
  client_secret:
    description: ""
    required: false
    type: str
  customer_id:
    description: ""
    required: false
    type: str
  name:
    description: "Name of the application segment."
    required: false
    type: str
  id:
    description: "ID of the application segment."
    required: False
    type: str
"""

EXAMPLES = """
- name: Retrieve Details of All Application Segments
  zscaler.zpacloud.zpa_application_segment_info:

- name: Retrieve Details of a Specific Application Segments by Name
  zscaler.zpacloud.zpa_application_segment_info:
    name: "Example Application Segment"

- name: Retrieve Details of a Specific Application Segments by ID
  zscaler.zpacloud.zpa_application_segment_info:
    id: "216196257331291981"
"""

RETURN = """
# Returns information on a specified Application Segment.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module: AnsibleModule):
    segment_id = module.params.get("id", None)
    segment_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    app_segments = []
    if segment_id is not None:
        segment_box = client.app_segments.get_segment(segment_id=segment_id)
        if segment_box is None:
            module.fail_json(
                msg="Failed to retrieve Application Segment ID: '%s'" % (segment_id)
            )
        app_segments = [segment_box.to_dict()]
    else:
        app_segments = client.app_segments.list_segments().to_list()
        if segment_name is not None:
            app_segment_found = False
            for app_segment in app_segments:
                if app_segment.get("name") == segment_name:
                    app_segment_found = True
                    app_segments = [app_segment]
            if not app_segment_found:
                module.fail_json(
                    msg="Failed to retrieve Application Segment Name: '%s'"
                    % (segment_name)
                )
    module.exit_json(changed=False, data=app_segments)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
