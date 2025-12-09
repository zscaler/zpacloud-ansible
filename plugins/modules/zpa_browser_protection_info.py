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
module: zpa_browser_protection_info
short_description: Retrieves Browser Protection Profile information.
description:
    - This module will allow the retrieval of information about a Browser Protection Profile.
    - Browser Protection Profiles are used to configure browser fingerprinting and protection settings.
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
      - The name of the Browser Protection Profile.
      - If not specified, returns the default/active browser protection profile.
    required: false
    type: str
"""

EXAMPLES = """
- name: Get Default/Active Browser Protection Profile
  zscaler.zpacloud.zpa_browser_protection_info:
    provider: "{{ zpa_cloud }}"

- name: Get Browser Protection Profile by Name
  zscaler.zpacloud.zpa_browser_protection_info:
    provider: "{{ zpa_cloud }}"
    name: "Zs Recommended profile"
"""

RETURN = r"""
profile:
  description: >-
    A dictionary containing details about the Browser Protection Profile.
  returned: always
  type: dict
  contains:
    id:
      description: The unique identifier of the Browser Protection Profile.
      type: str
      sample: "216199618143442006"
    name:
      description: The name of the Browser Protection Profile.
      type: str
      sample: "Zs Recommended profile"
    description:
      description: Additional information about the Browser Protection Profile.
      type: str
      sample: "Default recommended browser protection profile"
    default_csp:
      description: Whether to use the default Content Security Policy.
      type: bool
      sample: true
    creation_time:
      description: The creation time of the profile.
      type: str
      sample: "1632150400"
    modified_by:
      description: The ID of the user who last modified the profile.
      type: str
      sample: "216199618143442000"
    modified_time:
      description: The last modification time of the profile.
      type: str
      sample: "1632150400"
    criteria_flags_mask:
      description: The criteria flags mask used for browser protection matching.
      type: str
      sample: "65535"
    criteria:
      description: The criteria configuration for browser protection.
      type: list
      elements: dict
      contains:
        finger_print_criteria:
          description: Fingerprint criteria configuration.
          type: list
          elements: dict
          contains:
            collect_location:
              description: Whether to collect location information.
              type: bool
              sample: true
            fingerprint_timeout:
              description: Timeout in seconds for fingerprint collection.
              type: str
              sample: "30"
            browser:
              description: Browser fingerprinting settings.
              type: list
              elements: dict
              contains:
                browser_eng:
                  description: Collect browser engine information.
                  type: bool
                  sample: true
                browser_eng_ver:
                  description: Collect browser engine version.
                  type: bool
                  sample: true
                browser_name:
                  description: Collect browser name.
                  type: bool
                  sample: true
                browser_version:
                  description: Collect browser version.
                  type: bool
                  sample: true
                canvas:
                  description: Collect canvas fingerprinting data.
                  type: bool
                  sample: true
                flash_ver:
                  description: Collect Flash version.
                  type: bool
                  sample: false
                fp_usr_agent_str:
                  description: Collect user agent string.
                  type: bool
                  sample: true
                is_cookie:
                  description: Check for cookie support.
                  type: bool
                  sample: true
                is_local_storage:
                  description: Check for local storage support.
                  type: bool
                  sample: true
                is_sess_storage:
                  description: Check for session storage support.
                  type: bool
                  sample: true
                ja3:
                  description: Collect JA3 fingerprint.
                  type: bool
                  sample: true
                mime:
                  description: Collect MIME type information.
                  type: bool
                  sample: true
                plugin:
                  description: Collect plugin information.
                  type: bool
                  sample: true
                silverlight_ver:
                  description: Collect Silverlight version.
                  type: bool
                  sample: false
            location:
              description: Location collection settings.
              type: list
              elements: dict
              contains:
                lat:
                  description: Collect latitude.
                  type: bool
                  sample: true
                lon:
                  description: Collect longitude.
                  type: bool
                  sample: true
            system:
              description: System fingerprinting settings.
              type: list
              elements: dict
              contains:
                avail_screen_resolution:
                  description: Collect available screen resolution.
                  type: bool
                  sample: true
                cpu_arch:
                  description: Collect CPU architecture.
                  type: bool
                  sample: true
                curr_screen_resolution:
                  description: Collect current screen resolution.
                  type: bool
                  sample: true
                font:
                  description: Collect font information.
                  type: bool
                  sample: true
                java_ver:
                  description: Collect Java version.
                  type: bool
                  sample: false
                mobile_dev_type:
                  description: Collect mobile device type.
                  type: bool
                  sample: true
                monitor_mobile:
                  description: Monitor mobile devices.
                  type: bool
                  sample: true
                os_name:
                  description: Collect operating system name.
                  type: bool
                  sample: true
                os_version:
                  description: Collect operating system version.
                  type: bool
                  sample: true
                sys_lang:
                  description: Collect system language.
                  type: bool
                  sample: true
                tz:
                  description: Collect timezone information.
                  type: bool
                  sample: true
                usr_lang:
                  description: Collect user language.
                  type: bool
                  sample: true
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    collect_all_items,
)


def flatten_browser_criteria(browser):
    """Flatten the browser criteria nested structure."""
    if not browser:
        return []
    browser_dict = browser if isinstance(browser, dict) else browser
    return [{
        "browser_eng": browser_dict.get("browser_eng", False),
        "browser_eng_ver": browser_dict.get("browser_eng_ver", False),
        "browser_name": browser_dict.get("browser_name", False),
        "browser_version": browser_dict.get("browser_version", False),
        "canvas": browser_dict.get("canvas", False),
        "flash_ver": browser_dict.get("flash_ver", False),
        "fp_usr_agent_str": browser_dict.get("fp_usr_agent_str", False),
        "is_cookie": browser_dict.get("is_cookie", False),
        "is_local_storage": browser_dict.get("is_local_storage", False),
        "is_sess_storage": browser_dict.get("is_sess_storage", False),
        "ja3": browser_dict.get("ja3", False),
        "mime": browser_dict.get("mime", False),
        "plugin": browser_dict.get("plugin", False),
        "silverlight_ver": browser_dict.get("silverlight_ver", False),
    }]


def flatten_location_criteria(location):
    """Flatten the location criteria nested structure."""
    if not location:
        return []
    location_dict = location if isinstance(location, dict) else location
    return [{
        "lat": location_dict.get("lat", False),
        "lon": location_dict.get("lon", False),
    }]


def flatten_system_criteria(system):
    """Flatten the system criteria nested structure."""
    if not system:
        return []
    system_dict = system if isinstance(system, dict) else system
    return [{
        "avail_screen_resolution": system_dict.get("avail_screen_resolution", False),
        "cpu_arch": system_dict.get("cpu_arch", False),
        "curr_screen_resolution": system_dict.get("curr_screen_resolution", False),
        "font": system_dict.get("font", False),
        "java_ver": system_dict.get("java_ver", False),
        "mobile_dev_type": system_dict.get("mobile_dev_type", False),
        "monitor_mobile": system_dict.get("monitor_mobile", False),
        "os_name": system_dict.get("os_name", False),
        "os_version": system_dict.get("os_version", False),
        "sys_lang": system_dict.get("sys_lang", False),
        "tz": system_dict.get("tz", False),
        "usr_lang": system_dict.get("usr_lang", False),
    }]


def flatten_finger_print_criteria(fpc):
    """Flatten the finger print criteria nested structure."""
    if not fpc:
        return []
    fpc_dict = fpc if isinstance(fpc, dict) else fpc
    return [{
        "collect_location": fpc_dict.get("collect_location", False),
        "fingerprint_timeout": fpc_dict.get("fingerprint_timeout", ""),
        "browser": flatten_browser_criteria(fpc_dict.get("browser", {})),
        "location": flatten_location_criteria(fpc_dict.get("location", {})),
        "system": flatten_system_criteria(fpc_dict.get("system", {})),
    }]


def flatten_criteria(criteria):
    """Flatten the criteria nested structure."""
    if not criteria:
        return []
    criteria_dict = criteria if isinstance(criteria, dict) else criteria
    return [{
        "finger_print_criteria": flatten_finger_print_criteria(
            criteria_dict.get("finger_print_criteria", {})
        ),
    }]


def flatten_profile(profile):
    """Flatten the profile to a clean dictionary."""
    profile_dict = profile.as_dict() if hasattr(profile, "as_dict") else profile
    return {
        "id": profile_dict.get("id", ""),
        "name": profile_dict.get("name", ""),
        "description": profile_dict.get("description", ""),
        "default_csp": profile_dict.get("default_csp", False),
        "creation_time": profile_dict.get("creation_time", ""),
        "modified_by": profile_dict.get("modified_by", ""),
        "modified_time": profile_dict.get("modified_time", ""),
        "criteria_flags_mask": profile_dict.get("criteria_flags_mask", ""),
        "criteria": flatten_criteria(profile_dict.get("criteria", {})),
    }


def core(module):
    client = ZPAClientHelper(module)

    profile_name = module.params.get("name")

    # Fetch all browser protection profiles
    profiles, err = collect_all_items(
        client.browser_protection.list_browser_protection_profile, {}
    )
    if err:
        module.fail_json(msg=f"Error listing browser protection profiles: {to_native(err)}")

    if not profiles:
        module.fail_json(msg="No browser protection profiles found")

    # If name is specified, search for that profile
    if profile_name:
        matched_profile = None
        for profile in profiles:
            profile_dict = profile.as_dict() if hasattr(profile, "as_dict") else profile
            if profile_dict.get("name") == profile_name:
                matched_profile = profile
                break

        if not matched_profile:
            available = [p.as_dict().get("name") if hasattr(p, "as_dict") else p.get("name") for p in profiles]
            module.fail_json(
                msg=f"Couldn't find any browser protection profile with name '{profile_name}'. Available: {available}"
            )

        result = flatten_profile(matched_profile)
        module.exit_json(changed=False, profile=result)
    else:
        # Return the first (default/active) profile
        result = flatten_profile(profiles[0])
        module.exit_json(changed=False, profile=result)


def main():
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
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

