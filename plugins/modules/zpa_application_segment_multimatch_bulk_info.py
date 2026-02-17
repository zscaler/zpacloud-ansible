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
module: zpa_application_segment_multimatch_bulk_info
short_description: Retrieves unsupported multimatch references for domain names.
description:
    - This module retrieves application segments that cannot support multimatch for the specified domain names.
    - It identifies application segments with unsupported features when using multimatch functionality.
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
  domain_names:
    description:
      - List of domain names to check for unsupported multimatch references.
      - At least one domain name must be provided.
    required: true
    type: list
    elements: str
  microtenant_id:
    description:
      - The unique identifier of the Microtenant for the ZPA tenant.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Unsupported Multimatch References for Domains
  zscaler.zpacloud.zpa_application_segment_multimatch_bulk_info:
    provider: "{{ zpa_cloud }}"
    domain_names:
      - "app1.example.com"
      - "app2.example.com"

- name: Get Unsupported Multimatch References with Microtenant
  zscaler.zpacloud.zpa_application_segment_multimatch_bulk_info:
    provider: "{{ zpa_cloud }}"
    domain_names:
      - "myapp.securitygeek.io"
    microtenant_id: "216199618143373000"
"""

RETURN = r"""
unsupported_references:
  description: >-
    List of application segments that cannot support multimatch for the specified domains.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Application segment ID.
      type: str
      sample: "216199618143442000"
    app_segment_name:
      description: Application segment name.
      type: str
      sample: "MyAppSegment"
    domains:
      description: List of domain names for this segment.
      type: list
      elements: str
      sample: ["app1.example.com", "app2.example.com"]
    tcp_ports:
      description: List of TCP ports for this segment.
      type: list
      elements: str
      sample: ["8080", "443"]
    match_style:
      description: Current match style of the segment (EXCLUSIVE or INCLUSIVE).
      type: str
      sample: "EXCLUSIVE"
    microtenant_name:
      description: Microtenant name associated with this segment.
      type: str
      sample: "MyMicrotenant"
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def flatten_unsupported_references(references):
    """Flatten the unsupported references response."""
    if not references:
        return []

    result = []
    for ref in references:
        ref_dict = ref.as_dict() if hasattr(ref, "as_dict") else ref
        result.append(
            {
                "id": ref_dict.get("id", ""),
                "app_segment_name": ref_dict.get("app_segment_name", ""),
                "domains": ref_dict.get("domains", []),
                "tcp_ports": ref_dict.get("tcp_ports", []),
                "match_style": ref_dict.get("match_style", ""),
                "microtenant_name": ref_dict.get("microtenant_name", ""),
            }
        )
    return result


def core(module):
    client = ZPAClientHelper(module)

    domain_names = module.params.get("domain_names")
    microtenant_id = module.params.get("microtenant_id")

    if not domain_names or len(domain_names) == 0:
        module.fail_json(
            msg="At least one domain name must be provided in 'domain_names'"
        )

    # Get the unsupported multimatch references
    kwargs = {}
    if microtenant_id:
        kwargs["microtenant_id"] = microtenant_id

    references, _unused, error = (
        client.application_segment.get_multimatch_unsupported_references(
            domain_names, **kwargs
        )
    )
    if error:
        module.fail_json(
            msg=f"Failed to retrieve multimatch unsupported references: {to_native(error)}"
        )

    # Flatten and return the result
    flattened = flatten_unsupported_references(references or [])

    module.exit_json(
        changed=False, domain_names=domain_names, unsupported_references=flattened
    )


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        domain_names=dict(type="list", elements="str", required=True),
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
