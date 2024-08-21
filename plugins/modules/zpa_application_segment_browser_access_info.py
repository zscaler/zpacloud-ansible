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

DOCUMENTATION = r"""
---
module: zpa_application_segment_browser_access_info
short_description: Retrieves browser access application segment information.
description:
  - This module will allow the retrieval of information about a browser access application segment.
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
      - Name of the App Connector Group.
    required: false
    type: str
  id:
    description:
      - ID of the App Connector Group.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Gather information about all browser access application segments
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"

- name: Browser Access Application Segment by Name
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"
    name: "Example"

- name: Browser Access Application Segment by ID
  zscaler.zpacloud.zpa_application_segment_browser_access_info:
    provider: "{{ zpa_cloud }}"
    id: "198288282"
"""

RETURN = r"""
ba_app_segments:
  description: Details of the browser access application segments that match the criteria.
  returned: always
  type: list
  elements: dict
  contains:
    adp_enabled:
      description: Indicates if Advanced Data Protection (ADP) is enabled.
      type: bool
      sample: false
    api_protection_enabled:
      description: Indicates if API protection is enabled.
      type: bool
      sample: false
    auto_app_protect_enabled:
      description: Indicates if automatic application protection is enabled.
      type: bool
      sample: false
    bypass_on_reauth:
      description: Indicates if the application segment bypasses authentication on reauthorization.
      type: bool
      sample: false
    bypass_type:
      description: The type of bypass configured for the application segment.
      type: str
      sample: "NEVER"
    clientless_apps:
      description: List of clientless applications associated with the browser access application segment.
      type: list
      elements: dict
      contains:
        allow_options:
          description: Indicates if the OPTIONS HTTP method is allowed.
          type: bool
          sample: false
        app_id:
          description: The application ID associated with the clientless app.
          type: str
          sample: "216199618143442006"
        application_port:
          description: The port number of the application.
          type: str
          sample: "443"
        application_protocol:
          description: The protocol used by the application.
          type: str
          sample: "HTTPS"
        certificate_id:
          description: The ID of the certificate associated with the application.
          type: str
          sample: "216199618143247243"
        certificate_name:
          description: The name of the certificate associated with the application.
          type: str
          sample: "jenkins.bd-hashicorp.com"
        cname:
          description: The CNAME record associated with the application.
          type: str
          sample: "77644.********.h.p.zpa-app.net"
        domain:
          description: The domain name of the application.
          type: str
          sample: "app01.acme.com"
        enabled:
          description: Indicates if the clientless app is enabled.
          type: bool
          sample: true
        hidden:
          description: Indicates if the clientless app is hidden.
          type: bool
          sample: false
        id:
          description: The unique identifier of the clientless app.
          type: str
          sample: "216199618143442007"
        name:
          description: The name of the clientless app.
          type: str
          sample: "app01.acme.com"
        path:
          description: The path associated with the clientless app.
          type: str
          sample: "/"
        portal:
          description: Indicates if the clientless app is a portal.
          type: bool
          sample: false
        trust_untrusted_cert:
          description: Indicates if untrusted certificates are trusted.
          type: bool
          sample: true
    config_space:
      description: The configuration space of the application segment.
      type: str
      sample: "DEFAULT"
    creation_time:
      description: The time when the application segment was created, in epoch format.
      type: str
      sample: "1724127537"
    description:
      description: A description of the application segment.
      type: str
      sample: "app01"
    domain_names:
      description: A list of domain names associated with the application segment.
      type: list
      elements: str
      sample: ["app01.acme.com"]
    double_encrypt:
      description: Indicates if double encryption is enabled.
      type: bool
      sample: false
    enabled:
      description: Indicates if the application segment is enabled.
      type: bool
      sample: true
    fqdn_dns_check:
      description: Indicates if FQDN DNS checks are enabled.
      type: bool
      sample: false
    health_check_type:
      description: The type of health check configured for the application segment.
      type: str
      sample: "DEFAULT"
    health_reporting:
      description: The health reporting mode for the application segment.
      type: str
      sample: "ON_ACCESS"
    icmp_access_type:
      description: The ICMP access type for the application segment.
      type: str
      sample: "NONE"
    id:
      description: The unique identifier of the application segment.
      type: str
      sample: "216199618143442006"
    inspect_traffic_with_zia:
      description: Indicates if traffic inspection with ZIA is enabled.
      type: bool
      sample: false
    ip_anchored:
      description: Indicates if IP anchoring is enabled.
      type: bool
      sample: false
    is_cname_enabled:
      description: Indicates if CNAME is enabled for the application segment.
      type: bool
      sample: true
    is_incomplete_dr_config:
      description: Indicates if the application segment has an incomplete disaster recovery configuration.
      type: bool
      sample: false
    match_style:
      description: The match style of the application segment.
      type: str
      sample: "EXCLUSIVE"
    microtenant_name:
      description: The name of the microtenant associated with the application segment.
      type: str
      sample: "Default"
    modified_by:
      description: The ID of the user who last modified the application segment.
      type: str
      sample: "216199618143191041"
    modified_time:
      description: The time when the application segment was last modified, in epoch format.
      type: str
      sample: "1724128093"
    name:
      description: The name of the application segment.
      type: str
      sample: "app01"
    passive_health_enabled:
      description: Indicates if passive health monitoring is enabled.
      type: bool
      sample: true
    segment_group_id:
      description: The ID of the segment group associated with the application segment.
      type: str
      sample: "216199618143442005"
    segment_group_name:
      description: The name of the segment group associated with the application segment.
      type: str
      sample: "Example200"
    select_connector_close_to_app:
      description: Indicates if the connector closest to the application should be selected.
      type: bool
      sample: false
    server_groups:
      description: A list of server groups associated with the application segment.
      type: list
      elements: dict
      contains:
        config_space:
          description: The configuration space of the server group.
          type: str
          sample: "DEFAULT"
        creation_time:
          description: The time when the server group was created, in epoch format.
          type: str
          sample: "1724111999"
        dynamic_discovery:
          description: Indicates if dynamic discovery is enabled for the server group.
          type: bool
          sample: true
        enabled:
          description: Indicates if the server group is enabled.
          type: bool
          sample: true
        id:
          description: The unique identifier of the server group.
          type: str
          sample: "216199618143442001"
        modified_by:
          description: The ID of the user who last modified the server group.
          type: str
          sample: "216199618143191041"
        modified_time:
          description: The time when the server group was last modified, in epoch format.
          type: str
          sample: "1724111999"
        name:
          description: The name of the server group.
          type: str
          sample: "Example200"
    tcp_keep_alive:
      description: Indicates if TCP keep-alive is enabled for the application segment.
      type: str
      sample: "0"
    tcp_port_range:
      description: A list of TCP port ranges associated with the application segment.
      type: list
      elements: dict
      contains:
        from:
          description: The starting port in the range.
          type: str
          sample: "443"
        to:
          description: The ending port in the range.
          type: str
          sample: "443"
    tcp_port_ranges:
      description: A list of TCP port ranges as strings associated with the application segment.
      type: list
      elements: str
      sample: ["443", "443"]
    use_in_dr_mode:
      description: Indicates if the application segment is used in disaster recovery mode.
      type: bool
      sample: false
    weighted_load_balancing:
      description: Indicates if weighted load balancing is enabled.
      type: bool
      sample: false

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
    ba_appsegment_id = module.params.get("id", None)
    ba_appsegment_name = module.params.get("name", None)
    client = ZPAClientHelper(module)
    ba_app_segments = []
    if ba_appsegment_id is not None:
        ba_app_segment_box = client.app_segments.get_segment(
            segment_id=ba_appsegment_id
        )
        if ba_app_segment_box is None:
            module.fail_json(
                msg="Failed to retrieve Browser Access Application Segment ID: '%s'"
                % (ba_appsegment_id)
            )
        ba_app_segments = [ba_app_segment_box.to_dict()]
    else:
        ba_app_segments = client.app_segments.list_segments(pagesize=500).to_list()
        if ba_appsegment_name is not None:
            ba_app_segment_found = False
            for ba_app_segment in ba_app_segments:
                if ba_app_segment.get("name") == ba_appsegment_name:
                    ba_app_segment_found = True
                    ba_app_segments = [ba_app_segment]
                    break
            if not ba_app_segment_found:
                module.fail_json(
                    msg="Failed to retrieve Browser Access Certificate Name: '%s'"
                    % (ba_appsegment_name)
                )
    module.exit_json(changed=False, ba_app_segments=ba_app_segments)


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
