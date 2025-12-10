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
    AnsibleFailJson,
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
        for key, value in data.items():
            setattr(self, key, value)

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPolicyCapabilitiesAccessRuleV2Module(ModuleTestCase):
    """Unit tests for zpa_policy_capabilities_access_rule_v2 module."""

    SAMPLE_RULE = {
        "id": "123456",
        "name": "Test_Capabilities_Rule",
        "description": "Test Rule",
        "rule_order": "1",
        "order": 1,
        "conditions": [],
        "privileged_capabilities": {
            "file_upload": True,
            "file_download": True,
            "clipboard_copy": True,
            "clipboard_paste": True,
        },
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_rule(self, mock_client, mocker):
        """Test creating a new rule"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=([], None),
        )
        mock_client.policies.add_capabilities_rule_v2.return_value = (
            MockBox(self.SAMPLE_RULE), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Capabilities_Rule",
            description="Test Rule",
            privileged_capabilities={
                "file_upload": True,
                "file_download": True,
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_update_rule_by_name(self, mock_client, mocker):
        """Test updating an existing rule by name"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.update_capabilities_rule_v2.return_value = (
            MockBox({**self.SAMPLE_RULE, "description": "Updated"}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Capabilities_Rule",
            description="Updated description",
            privileged_capabilities={
                "file_upload": True,
                "file_download": False,
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_delete_rule(self, mock_client, mocker):
        """Test deleting a rule"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=([MockBox(self.SAMPLE_RULE)], None),
        )
        mock_client.policies.delete_rule.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Capabilities_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert result.value.result["changed"] is True

    def test_delete_nonexistent_rule(self, mock_client, mocker):
        """Test deleting a nonexistent rule"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert result.value.result["changed"] is False

    def test_list_rules_error(self, mock_client, mocker):
        """Test error when listing rules"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Rule",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleFailJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert "error" in result.value.result["msg"].lower()

    def test_check_mode(self, mock_client, mocker):
        """Test check mode"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_policy_capabilities_access_rule_v2.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Rule",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_policy_capabilities_access_rule_v2

        with pytest.raises(AnsibleExitJson) as result:
            zpa_policy_capabilities_access_rule_v2.main()

        assert result.value.result["changed"] is True
