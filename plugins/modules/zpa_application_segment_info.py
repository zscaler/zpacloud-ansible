#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2023, Zscaler, Inc

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
