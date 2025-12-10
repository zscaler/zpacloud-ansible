# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)

from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPolicyAccessForwardingRuleModule(ModuleTestCase):
    """Unit tests for zpa_policy_access_forwarding_rule module."""

    SAMPLE_RULE = {
        "id": "216199618143441990",
        "name": "Test_Forwarding_Rule",
        "description": "Test Forwarding Rule",
        "action": "BYPASS",
        "rule_order": "1",
        "conditions": [],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_client_forwarding_rule.return_value = (MockBox(self.SAMPLE_RULE), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule",
            description="Test Forwarding Rule",
            action="BYPASS",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_forwarding_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule.main()

        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Forwarding_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_forwarding_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule.main()

        assert result.value.result["changed"] is True

    def test_rule_already_exists(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Forwarding_Rule",
            description="Test Forwarding Rule",
            action="BYPASS",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_forwarding_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule.main()

        assert result.value.result["changed"] is False

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_access_forwarding_rule.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_access_forwarding_rule

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_access_forwarding_rule.main()

        assert result.value.result["changed"] is False
