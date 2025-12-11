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
module: zpa_risk_score_values_info
short_description: Retrieves Risk Score Values.
description:
    - This module will allow the retrieval of Risk Score Values.
    - Risk Score Values are used in policy conditions for access control based on user risk.
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
  exclude_unknown:
    description:
      - If True, excludes UNKNOWN from the returned list of risk score values.
    required: false
    type: bool
    default: false
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant.
      - If not set, the default microtenant will be used.
    type: str
    required: false
"""

EXAMPLES = """
- name: Get All Risk Score Values
  zscaler.zpacloud.zpa_risk_score_values_info:
    provider: "{{ zpa_cloud }}"
  register: risk_scores

- name: Display Risk Score Values
  ansible.builtin.debug:
    var: risk_scores.values

- name: Get Risk Score Values Excluding UNKNOWN
  zscaler.zpacloud.zpa_risk_score_values_info:
    provider: "{{ zpa_cloud }}"
    exclude_unknown: true
  register: risk_scores_filtered
"""

RETURN = r"""
values:
  description: >-
    A list of risk score values available for use in policy conditions.
  returned: always
  type: list
  elements: str
  sample:
    - "CRITICAL"
    - "HIGH"
    - "MEDIUM"
    - "LOW"
    - "UNKNOWN"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def core(module):
    client = ZPAClientHelper(module)

    exclude_unknown = module.params.get("exclude_unknown")
    microtenant_id = module.params.get("microtenant_id")

    # Build query params
    query_params = {}
    if exclude_unknown:
        query_params["exclude_unknown"] = exclude_unknown
    if microtenant_id:
        query_params["microtenant_id"] = microtenant_id

    # Fetch risk score values
    values, _unused, err = client.policies.get_risk_score_values(query_params=query_params if query_params else None)
    if err:
        module.fail_json(msg=f"Error retrieving risk score values: {to_native(err)}")

    if values is None:
        values = []

    module.exit_json(changed=False, values=values)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        exclude_unknown=dict(type="bool", required=False, default=False),
        microtenant_id=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
