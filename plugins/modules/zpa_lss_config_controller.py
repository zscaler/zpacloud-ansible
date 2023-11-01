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
module: zpa_lss_config_controller
short_description: Create a LSS CONFIG.
description:
  - This module create/update/delete a LSS CONFIG in the ZPA Cloud.
author:
  - William Guilherme (@willguibr)
version_added: "1.0.0"
requirements:
    - Zscaler SDK Python can be obtained from PyPI U(https://pypi.org/project/zscaler-sdk-python/)
extends_documentation_fragment:
    - zscaler.zpacloud.fragments.credentials_set
    - zscaler.zpacloud.fragments.provider
    - zscaler.zpacloud.fragments.enabled_state
options:
  config:
    type: dict
    required: False
    description: "Name of the LSS configuration"
    suboptions:
      audit_message:
        description: ""
        type: str
        required: False
      description:
        description: "Name of the LSS configuration"
        type: str
        required: False
      enabled:
        description: "Whether this LSS configuration is enabled or not"
        type: bool
        required: False
        default: True
      filter:
        description: "Filter for the LSS configuration"
        type: list
        elements: str
        required: False
      source_log_format:
        description: "Format of the log type"
        type: str
        required: True
        choices:
          - json
          - csv
          - tsv
      id:
        description: ""
        type: str
      name:
        description: "Name of the LSS configuration"
        type: str
        required: True
      lss_host:
        description: "Host of the LSS configuration"
        type: str
        required: True
      lss_port:
        description: "Port of the LSS configuration"
        type: str
        required: True
      source_log_type:
        description: "Log type of the LSS configuration"
        type: str
        required: True
        choices:
          - app_connector_metrics
          - app_connector_status
          - audit_logs
          - browser_access
          - private_svc_edge_status
          - user_activity
          - user_status
      use_tls:
        description: "Whether TLS is enabled or not"
        type: bool
        required: False
        default: False
  app_connector_group_ids:
    type: list
    elements: str
    required: False
    description: "App Connector Group(s) to be added to the LSS configuration"
  id:
    type: str
    description: ""
  policy_rule_resource:
    type: dict
    description: "Object Type"
    required: False
    suboptions:
      action:
        description: ""
        type: str
        required: False
      action_id:
        description: ""
        type: str
        required: False
      description:
        description: "Object Type"
        type: str
        required: False
      priority:
        description: ""
        type: str
        required: False
      reauth_idle_timeout:
        description: ""
        type: str
        required: False
      policy_type:
        description: ""
        type: str
        required: False
      reauth_default_rule:
        description: ""
        type: bool
        required: False
      custom_msg:
        description: ""
        type: str
        required: False
      operator:
        description: ""
        type: str
        required: False
      bypass_default_rule:
        description: ""
        type: bool
        required: False
      policy_set_id:
        description: ""
        type: str
        required: False
      default_rule:
        description: ""
        type: bool
        required: False
      name:
        description: ""
        type: str
        required: True
      reauth_timeout:
        description: ""
        type: str
        required: False
      rule_order:
        description: ""
        type: str
        required: False
      id:
        description: ""
        type: str
      lss_default_rule:
        description: ""
        type: bool
        required: False
      conditions:
        description: ""
        type: list
        elements: dict
        required: False
        suboptions:
          negated:
            description: ""
            type: bool
            required: False
          operator:
            description: ""
            type: str
            required: True
          operands:
            description: ""
            type: list
            elements: dict
            required: False
            suboptions:
              values:
                description: ""
                type: list
                elements: str
                required: False
              object_type:
                description: ""
                type: str
                required: True
                choices: ["APP", "APP_GROUP", "CLIENT_TYPE"]
"""
EXAMPLES = """
- name: LSS Controller
  hosts: localhost
  tasks:
    - name: Create a LSS Controller
      zscaler.zpacloud.zpa_lss_config_controller:
        provider: "{{ zpa_cloud }}"
        config:
          name: Status
          description: status
          enabled: true
          lss_host: 10.1.1.1
          lss_port: 20000
          format: "..."
          source_log_type: "zpn_ast_auth_log"
        app_connector_group_ids:
          - "11111"
      register: lss_controller
    - name: lss_controller
      debug:
        msg: "{{ lss_controller }}"
"""

RETURN = """
# The newly created policy access rule resource record.
"""

from traceback import format_exc

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.zscaler.zpacloud.plugins.module_utils.utils import (
    deleteNone,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)


def get_lss_config(id, client):
    confs = client.lss.list_configs().to_list()
    for lssconf in confs:
        if lssconf.get("config").get("id") == id:
            return lssconf


def core(module):
    state = module.params.get("state", None)
    client = ZPAClientHelper(module)
    lss_config = dict()
    params = ["id", "config", "app_connector_group_ids", "policy_rule_resource"]
    for param_name in params:
        lss_config[param_name] = module.params.get(param_name, None)
    lss_config_name = lss_config.get("config", {}).get("name")
    lss_config_id = lss_config.get("id")
    existing_lss_config = None
    if lss_config_id is not None:
        existing_lss_config = client.lss.get_config(lss_id=lss_config_id)
    elif lss_config_name is not None:
        confs = client.lss.list_configs().to_list()
        for lssconf in confs:
            if lssconf.get("config").get("name") == lss_config_name:
                existing_lss_config = lssconf
                break
    if existing_lss_config is not None:
        id = existing_lss_config.get("id")
        existing_lss_config.update(lss_config)
        existing_lss_config["id"] = id
    if state == "present":
        if existing_lss_config is not None:
            policy_rule_resource = existing_lss_config.get("policy_rule_resource", None)
            policy_rules = []
            if policy_rule_resource is not None:
                policy_rules.append(policy_rule_resource)
            """Update"""
            existing_lss_config = deleteNone(
                dict(
                    lss_config_id=existing_lss_config.get("id", None),
                    description=existing_lss_config.get("config", dict()).get(
                        "description", None
                    ),
                    enabled=existing_lss_config.get("config", dict()).get(
                        "enabled", None
                    ),
                    filter_status_codes=existing_lss_config.get("config", dict()).get(
                        "filter_status_codes", None
                    ),
                    log_stream_content=existing_lss_config.get("config", dict()).get(
                        "log_stream_content", None
                    ),
                    source_log_format=existing_lss_config.get("config", dict()).get(
                        "source_log_format", None
                    ),
                    source_log_type=existing_lss_config.get("config", dict()).get(
                        "source_log_type", None
                    ),
                    use_tls=existing_lss_config.get("config", dict()).get(
                        "use_tls", None
                    ),
                    policy_rules=policy_rules,
                )
            )
            lss_config = client.lss.update_lss_config(**existing_lss_config)
            module.exit_json(
                changed=True, data=get_lss_config(lss_config.get("id"), client)
            )
        else:
            """Create"""
            policy_rule_resource = lss_config.get("policy_rule_resource", None)
            policy_rules = []
            if policy_rule_resource is not None:
                policy_rules.append(policy_rule_resource)
            lss_config = deleteNone(
                dict(
                    app_connector_group_ids=lss_config.get(
                        "app_connector_group_ids", None
                    ),
                    enabled=lss_config.get("config", dict()).get("enabled", None),
                    lss_host=lss_config.get("config", dict()).get("lss_host", None),
                    lss_port=lss_config.get("config", dict()).get("lss_port", None),
                    name=lss_config.get("config", dict()).get("name", None),
                    source_log_format=lss_config.get("config", dict()).get(
                        "source_log_format", None
                    ),
                    source_log_type=lss_config.get("config", dict()).get(
                        "source_log_type", None
                    ),
                    use_tls=lss_config.get("config", dict()).get("use_tls", None),
                    description=lss_config.get("config", dict()).get(
                        "description", None
                    ),
                    filter_status_codes=lss_config.get("config", dict()).get(
                        "filter", None
                    ),
                    log_stream_content=lss_config.get("config", dict()).get(
                        "log_stream_content", None
                    ),
                    policy_rules=policy_rules,
                )
            )
            lss_config = client.lss.add_lss_config(**lss_config)
            module.exit_json(
                changed=True, data=get_lss_config(lss_config.get("id"), client)
            )
    elif state == "absent" and existing_lss_config is not None:
        code = client.lss.delete_lss_config(lss_id=existing_lss_config.get("id"))
        if code > 299:
            module.exit_json(changed=False, data=None)
        module.exit_json(changed=True, data=existing_lss_config)
    module.exit_json(changed=False, data={})


def main():
    """Main"""
    argument_spec = ZPAClientHelper.zpa_argument_spec()
    argument_spec.update(
        id=dict(type="str"),
        policy_rule_resource=dict(
            type="dict",
            options=dict(
                priority=dict(type="str", required=False),
                reauth_idle_timeout=dict(type="str", required=False),
                policy_type=dict(type="str", required=False),
                reauth_default_rule=dict(type="bool", required=False),
                custom_msg=dict(type="str", required=False),
                action_id=dict(type="str", required=False),
                operator=dict(type="str", required=False),
                bypass_default_rule=dict(type="bool", required=False),
                policy_set_id=dict(type="str", required=False),
                default_rule=dict(type="bool", required=False),
                action=dict(type="str", required=False),
                conditions=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        negated=dict(type="bool", required=False),
                        operator=dict(type="str", required=True),
                        operands=dict(
                            type="list",
                            elements="dict",
                            options=dict(
                                values=dict(
                                    type="list", elements="str", required=False
                                ),
                                object_type=dict(
                                    type="str",
                                    required=True,
                                    choices=["APP", "APP_GROUP", "CLIENT_TYPE"],
                                ),
                            ),
                            required=False,
                        ),
                    ),
                    required=False,
                ),
                name=dict(type="str", required=True),
                reauth_timeout=dict(type="str", required=False),
                rule_order=dict(type="str", required=False),
                description=dict(type="str", required=False),
                id=dict(type="str"),
                lss_default_rule=dict(type="bool", required=False),
            ),
            required=False,
        ),
        app_connector_group_ids=dict(
            type="list",
            elements="str",
            required=False,
        ),
        config=dict(
            type="dict",
            options=dict(
                source_log_format=dict(
                    type="str",
                    choices=[
                        "json",
                        "csv",
                        "tsv",
                    ],
                    required=False,
                ),
                id=dict(type="str"),
                name=dict(type="str", required=True),
                audit_message=dict(type="str", required=False),
                lss_port=dict(type="str", required=True),
                lss_host=dict(type="str", required=True),
                use_tls=dict(type="bool", required=False, default=False),
                enabled=dict(type="bool", required=False, default=True),
                description=dict(type="str", required=False),
                filter=dict(type="list", elements="str", required=False),
                source_log_type=dict(
                    type="str",
                    required=True,
                    choices=[
                        "",
                        "app_connector_metrics",
                        "app_connector_status",
                        "audit_logs",
                        "browser_access",
                        "private_svc_edge_status",
                        "user_activity",
                        "user_status",
                        "web_inspection",
                    ],
                ),
            ),
            required=False,
        ),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == "__main__":
    main()
